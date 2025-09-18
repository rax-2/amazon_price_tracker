# Advanced Automated Python Billing System
# Copyright (C) 2025 Rakesh (AKA Pinaka)
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See LICENSE file for details.


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import UpdateOne
from requests import get
from bs4 import BeautifulSoup
from time import sleep
from rich import traceback
from rich.console import Console
from os import getenv
from dotenv import load_dotenv

traceback.install()
console = Console()

load_dotenv()
uri = getenv("MONGO_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))
db = client["products"]
coll = db["items"]


def getWishlist() -> list:
    """db theke sob wishlisted item gulo ke niye ase"""
    data = coll.find({})
    return list(data)


def getProduct(url: str) -> list:
    """amazon tekhe scrape kore prduct er price anche"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    res = get(url, headers=headers)

    if res.status_code != 200:
        print(f"Failed to fetch: {url}")
        return ["Unavailable", 0]

    soup = BeautifulSoup(res.text, "html.parser")

    try:
        product_title = soup.find("span", id="productTitle").get_text(strip=True)
        price_tag = soup.find("span", class_="a-price-whole")
        if not price_tag:
            print("Price not found")
            return [product_title, 0]
        current_price = price_tag.get_text().replace(",", "").replace(".", "")
        return [product_title, int(current_price)]
    except Exception as e:
        print(f"Error parsing product data: {e}")
        return ["Unavailable", 0]


def updateDb(data: list) -> None:
    """New price db te save kore"""
    operation = []
    for item in data:
        operation.append(
            UpdateOne({"_id": item["_id"]}, {"$set": {"nprice": item["nprice"]}})
        )
    coll.bulk_write(operation)


def updatePrice() -> None:
    updates = []
    wishlist = getWishlist()
    for item in wishlist:
        name, currentPrice = getProduct(url=item.get("url"))
        try:
            if currentPrice != int(item.get("nprice")):
                print("price change")
                item["nprice"] = currentPrice
                updates.append(item)
            else:
                pass
        except Exception as e:
            print(e)

    updateDb(updates) if updates else print("no Price change")


def main():
    while True:
        updatePrice()
        for i in range(60):
            print(f"{i}", end="\r")
            sleep(1)


main()
