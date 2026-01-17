from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/"
}

def resolve_short_url(url):
    """
    Bắt redirect thật từ link tiktok.com/t/
    """
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            allow_redirects=True,
            timeout=10
        )
        return r.url
    except:
        return url


def extract_product(url):
    try:
        final_url = resolve_short_url(url)

        r = requests.get(
            final_url,
            headers=HEADERS,
            timeout=15
        )

        soup = BeautifulSoup(r.text, "html.parser")

        title_tag = soup.find("meta", property="og:title")
        image_tag = soup.find("meta", property="og:image")

        title = title_tag["content"] if title_tag else "Không lấy được tiêu đề"
        image = image_tag["content"] if image_tag else "Không lấy được ảnh"

        return {
            "product_url": final_url,
            "title": title,
            "image": image
        }

    except Exception as e:
        return {
            "product_url": url,
            "title": f"Lỗi: {str(e)}",
            "image": ""
        }


@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    if request.method == "POST":
        raw_links = request.form.get("links", "")
        links = [l.strip() for l in raw_links.splitlines() if l.strip()]

        for link in links:
            results.append(extract_product(link))

    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
