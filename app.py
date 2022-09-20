from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin   #flask_cors - is used to domain of both the resources are differenr
import requests #module allows you to send HTTP requests & returns a Response Object with all the response data (content, encoding, status, etc).
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq #used to open the urls

app =Flask(__name__)
git config --global user.email "03ankitaramvirsingh@gmail.com"
# route to display the home page
@app.route('/',methods = ['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')

#route to show all the reviews on webpage
@app.route('/review',methods = ['GET','POST'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:

            searchstring = request.form['content'].replace(' ','')
            flipkart_url = "https://www.flipkart.com/search?q=" +searchstring
            print(flipkart_url)
# since we can extract all the reviews from 1 bigbox -- I have used bigvoxes[0] ie 1st bigbox
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage,'html.parser')

            bigboxes = flipkart_html.find_all('div',{'class':'_2kHMtA'})
            href = 'https://www.flipkart.com'+bigboxes[0].a['href']
            uClient = uReq(href)
            page = uClient.read()
            uClient.close()
            page_html = bs(page,'html.parser')

#then once entered in 1st bigbox go to view all review -- currently approx 7000 reviews
            #review url for page 1
            z = page_html.find_all('a', {'class': ''})
            href = []
            for i in z:
                href.append(i.get('href'))
            for j in href:
                if 'LSTMOBFWQ6BVWVEH3XEMXQMLO' in j:
                    page = 'https://www.flipkart.com' + j
                    print(page)

            #now collect all the urls -  there are 704 pages, therefore collect all the 704 urls

#after looking into all the pages manually -- only 1st 100 pages have reviews
            l = []
            try:
                for i in range(1,101):
                    pagination = (page +'&page=' + str(i))
                    l.append(pagination)
            except Exception as e:
                print(e)

#creating csv files for which ever product is searched
            filename = searchstring + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Date, Rating, Heading, Comment \n"
            fw.write(headers)
#read content from all the 100 urls
            reviews = []
            counter = 0
            ratings = []
            review_headers = []
            review = []
            names = []

            while counter < len(l):
                r = requests.get(l[counter])
                beutifiyed_html = bs(r.text, 'html.parser')
#ratings
                try:
                    all_rating = beutifiyed_html.find_all('div', attrs={'class': '_1BLPMq'})
                    for i in all_rating:
                        ratings.append(i.text)
                except:
                    no_rating = 'No Rating'
                    ratings.append(no_rating)
#comment headers
                try:
                    review_heading = beutifiyed_html.find_all('p', {'class': "_2-N8zT"})
                    for i in review_heading:
                        review_headers.append(i.text)
                except:
                    no_header = 'No header'
                    review_headers.append(no_header)
#review
                try:
                    review = beutifiyed_html.find_all('div', {'class': 't-ZTKy'})
                    for i in review:
                        review.append(i.text)
                except:
                    no_review = 'No Review'
                    review.append(no_review)
#names
                try:
                    all_names = beutifiyed_html.find_all('p', {"class": "_2sc7ZR _2V5EHH"})
                    for i in all_names:
                        names.append(i.text)
                except:
                    no_name = 'No Name'
                    names.append(no_name)


                counter = counter + 1
            mydict = {"Product": searchstring, "Name": names,  "Rating": ratings, "CommentHead": review_headers,"Comment": review}
            reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])

        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)