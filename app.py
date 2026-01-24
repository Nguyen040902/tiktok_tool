from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

SCRAPER_API_KEY = "14d6abce756a7b98fb2f085fc4e48801"

def scrape_url(url):
    api_url = "http://api.scraperapi.com"
    params = {
        "api_key": SCRAPER_API_KEY,
        "url": url,
        "render": "false",
        "country_code": "us"
    }
    r = requests.get(api_url, params=params, timeout=20)
    return r.text

def extract_product(url):
    try:
        html = scrape_url(url)
        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.find("meta", property="og:title")
        image_tag = soup.find("meta", property="og:image")

        if not title_tag or not image_tag:
            return None

        title = title_tag["content"]
        image = image_tag["content"].split("?")[0]

        return {
            "title": title,
            "image": image,
            "product_url": url
        }
    except:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fetch", methods=["POST"])
def fetch():
    urls = request.json.get("urls", [])
    results = []

    for url in urls:
        data = extract_product(url)
        if data:
            results.append(data)

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
