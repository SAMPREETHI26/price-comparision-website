from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import pandas as pd

app = Flask(__name__)

# Function to scrape data from Flipkart
def scrape_flipkart(search_query):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    flipkart_url = f"https://www.flipkart.com/search?q={search_query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&as-pos=1&as-type=HISTORY"
    flipkart_response = requests.get(flipkart_url, headers=HEADERS)
    
    if flipkart_response.status_code == 200:
        flipkart_soup = BeautifulSoup(flipkart_response.content, 'lxml')
        flipkart_products = flipkart_soup.find_all('div', {'class': '_1AtVbE col-12-12'})

        flipkart_results = []

        for product in flipkart_products:
            name = product.find('div', {'class': '_4rR01T'})
            price = product.find('div', {'class': '_30jeq3 _1_WHN1'})
            rating = product.find('div', {'class': '_3LWZlK'})

            if name and price:
                product_name = name.text
                product_price = price.string.strip()
                product_rating = rating.get_text(strip=True) if rating else "N/A"
                flipkart_results.append({'name': product_name, 'price': product_price, 'rating': product_rating})

        return flipkart_results
    else:
        return []

# Function to scrape data from Amazon
def scrape_amazon(search_query):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
        'Accept-Language': 'en-US, en;q=0.5'
    }

    amazon_url = f"https://www.amazon.in/s?k={search_query}&crid=1J225A6EKXQLE&sprefix=%2Caps%2C220&ref=nb_sb_ss_recent_1_0_recent"
    amazon_response = requests.get(amazon_url, headers=HEADERS)
    
    if amazon_response.status_code == 200:
        amazon_soup = BeautifulSoup(amazon_response.content, 'lxml')
        amazon_products = amazon_soup.find_all('div', {'data-component-type': 's-search-result'})

        amazon_results = []

        for product in amazon_products:
            name = product.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
            price = product.find('span', {'class': 'a-price-whole'})
            rating = product.find('span', {'class': 'a-icon-alt'})

            if name and price:
                product_name = name.string.strip()
                product_price = price.string.strip()
                product_rating = rating.string.strip()
                amazon_results.append({'name': product_name, 'price': product_price, 'rating': product_rating})

        return amazon_results
    else:
        return []

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        search_query = request.form["nm"]

        flipkart_results = scrape_flipkart(search_query)
        amazon_results = scrape_amazon(search_query)

        # Create DataFrames
        flipkart_df = pd.DataFrame(flipkart_results)
        amazon_df = pd.DataFrame(amazon_results)

        return render_template('index.html', flipkart_df=flipkart_df, amazon_df=amazon_df)
    else:
        return render_template("open.html")

if __name__ == "__main__":
    app.run(debug=True)
