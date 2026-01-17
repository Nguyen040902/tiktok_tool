from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import random
import re
import os

app = Flask(__name__)

# ===== DANH SÁCH PROXY CỦA BẠN =====
PROXY_LIST = [
    "http://9KibdPTGKRD7f3L:bpr9Oz45bdzgss7@149.19.159.154:47309",
    "http://sunxft7l8lW9E4j:DLZCEmRO1zMmkEb@64.29.86.166:46952",
    "http://f8TvG5p2co4wg6O:MTkJU10xib0cwe4@64.29.86.237:44642"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/"
}

def get_random_proxy():
    proxy = random.choice(PROXY_LIST)
    return {"http": proxy, "https": proxy}

def extract_product(url):
    session = requests.Session()

    for _ in range(3):  # thử tối đa 3 proxy nếu lỗi
        proxy = get_random_proxy()

        try:
            r1 = session.get(url, headers=HEADERS, proxies=proxy, allow_redirects=True, timeout=15)
            final_url = r1.url

            if "view/product" in final_url:
                final_url = final_url.split("?")[0] + "?_web_embedded=1"

            r2 = session.get(final_url, headers=HEADERS, proxies=proxy, timeout=15)
            soup = BeautifulSoup(r2.text, "html.parser")

            title_tag = soup.find("meta", property="og:title")
            image_tag = soup.find("meta", property="og:image")

            if not title_tag or not image_tag:
                continue  # proxy bị TikTok chặn → thử proxy khác

            return {
                "product_url": final_url,
                "title": title_tag["content"],
                "image": image_tag["content"]
            }

        except:
            continue

    return {
        "product_url": url,
        "title": "Proxy bị TikTok chặn / không lấy được dữ liệu",
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
