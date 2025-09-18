# Advanced Automated Python Billing System
# Copyright (C) 2025 Rakesh (AKA Pinaka)
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See LICENSE file for details.


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from os import getenv
from dotenv import load_dotenv
from rich import traceback
from rich.console import Console
from requests import get
from bs4 import BeautifulSoup
from bson import ObjectId
from fastapi import FastAPI
from pydantic import BaseModel

traceback.install()
console = Console()

load_dotenv()
uri = getenv("MONGO_URI")

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


def addDB(product_title: str, url: str, product_price: int):
    status = coll.insert_one(
        {
            "name": product_title,
            "url": url,
            "sdprice": product_price,
            "nprice": product_price,
        }
    )
    return str(status.inserted_id)


def addProduct(url: str):
    product_title, product_price = getProduct(url=url)
    status = addDB(product_price=product_price, product_title=product_title, url=url)
    return status


def showProduct():
    dou = coll.find({}, {"_id": 1, "name": 1})
    data = []
    for doc in dou:
        doc["_id"] = str(doc["_id"])  # convert ObjectId to string
        data.append(doc)
    print(data)
    return data


def showAllProduct() -> list:
    dou = coll.find({})
    data = []
    for doc in dou:
        doc["_id"] = str(doc["_id"])  # convert ObjectId to string
        data.append(doc)
    console.print(data)
    return data


def showOne(id: str):
    dou = coll.find_one({"_id": ObjectId(id)}, {"_id": 0})
    return dou


def removeOneProduct(id: str):
    res = coll.delete_one({"_id": ObjectId(id)})
    console.print(res.deleted_count)
    console.print(f" [bold red] Removed product Sucessfully... [/bold red]")
    return res.deleted_count


app = FastAPI()


class Itemurl(BaseModel):
    url: str = None


class Itemremove(BaseModel):
    id: str


@app.get("/")
def home():
    return {"hello": "wellcome"}


@app.get("/products")
def products():
    data = showProduct()
    return data


@app.get("/allproducts")
def aallproducts():
    data = showAllProduct()
    return data


@app.post("/add")
def add(url: Itemurl):
    if url.url:
        status = addProduct(url.url)
        return {"status": str(status)}
    else:
        return {"status": 400, "comment": "no payload found"}


@app.get("/view")
def view(id: str):
    data = showOne(id)
    console.print(data)
    return {"status": 200, "item": data}


@app.post("/remove")
def remove(item: Itemremove):
    print(item.id)
    status = removeOneProduct(item.id)
    return {"ststus": status}



