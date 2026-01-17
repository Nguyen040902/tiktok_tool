from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)

def extract_product(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.tiktok.com/"
    }

    try:
        r = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
        html = r.text

        soup = BeautifulSoup(html, "html.parser")

        title_tag = soup.find("meta", property="og:title")
        image_tag = soup.find("meta", property="og:image")

        title = title_tag["content"] if title_tag else "Không lấy được tiêu đề"
        image = image_tag["content"] if image_tag else "Không lấy được ảnh"

        return {
            "url": url,
            "title": title,
            "image": image
        }

    except Exception as e:
        return {
            "url": url,
            "title": f"Lỗi: {str(e)}",
            "image": "—"
        }


@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    if request.method == "POST":
        raw = request.form.get("links")
        links = re.split(r"\n+", raw.strip())

        for link in links:
            results.append(extract_product(link.strip()))

    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
