from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "Connection": "keep-alive"
}

session = requests.Session()
session.headers.update(HEADERS)


def resolve_link(url):
    try:
        r = session.get(url, allow_redirects=True, timeout=15)
        return r.url
    except:
        return url


def extract_product_data(url):
    try:
        r = session.get(url, timeout=8)  # giảm timeout

        # Nếu TikTok trả trang chống bot → thường rất ngắn hoặc rất dài bất thường
        if len(r.text) < 3000:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        title_tag = soup.find("meta", property="og:title")
        image_tag = soup.find("meta", property="og:image")

        if not title_tag or not image_tag:
            return None

        title = title_tag.get("content", "").strip()
        image = image_tag.get("content", "").split("?")[0]

        return {
            "title": title,
            "image": image,
            "product_url": url
        }

    except requests.exceptions.Timeout:
        return None
    except:
        return None


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/fetch", methods=["POST"])
def fetch():
    urls = request.json.get("urls", [])
    results = []

    for url in urls:
        real_url = resolve_link(url)
        data = extract_product_data(real_url)
        if data:
            results.append(data)

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

