from flask import Flask, render_template, request, jsonify
import requests
import urllib.parse
import json
import webbrowser
import threading

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def resolve_link(url):
    r = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
    return r.url

def extract_product(real_url):
    parsed = urllib.parse.urlparse(real_url)
    qs = urllib.parse.parse_qs(parsed.query)

    if "og_info" not in qs:
        return None

    og = json.loads(urllib.parse.unquote(qs["og_info"][0]))

    title = og.get("title", "")
    image = og.get("image", "")

    if not title or not image:
        return None

    return {
        "title": title,
        "image": image,
        "product_url": real_url
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        urls = request.json.get("urls", [])
        results = []

        for url in urls:
            try:
                real = resolve_link(url)
                product = extract_product(real)
                if product:
                    results.append(product)
            except:
                pass

        return jsonify(results)

    return render_template("index.html")

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

