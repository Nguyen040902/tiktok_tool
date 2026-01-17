from flask import Flask, render_template, request
import requests
import json
import re

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}


def extract_product_data(url):
    try:
        html = requests.get(url, headers=HEADERS, timeout=15).text

        match = re.search(r'__UNIVERSAL_DATA_FOR_REHYDRATION__ = ({.*});', html)
        if not match:
            return []

        data = json.loads(match.group(1))

        product = data["__DEFAULT_SCOPE__"]["webapp.product-detail"]["product"]
        title = product["title"]

        sku_props = product.get("skuProps", [])
        sku_images = product.get("skuImages", {})

        results = []

        for prop in sku_props:
            if prop["propName"].lower() == "color":
                for value in prop["values"]:
                    color_name = value["name"]
                    sku_id = value["vid"]

                    image_list = sku_images.get(str(sku_id), [])
                    image_url = image_list[0] if image_list else ""

                    results.append({
                        "title": title,
                        "color": color_name,
                        "image": image_url
                    })

        return results

    except Exception as e:
        print("ERROR:", e)
        return []


@app.route("/", methods=["GET", "POST"])
def index():
    products = []
    if request.method == "POST":
        urls = request.form["urls"].splitlines()
        for url in urls:
            if url.strip():
                products.extend(extract_product_data(url.strip()))

    return render_template("index.html", products=products)


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
