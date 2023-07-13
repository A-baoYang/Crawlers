from bs4 import BeautifulSoup
import datetime as dt
import json
import logging
import numpy as np
import os
import pandas as pd
import requests
import re
import random
from tqdm import tqdm
import time
import urllib.parse


def getAllCompanies(filepath):
    """取得公司編號"""
    stock_ids = pd.read_csv(filepath, header=None)
    stock_ids.columns = ["comp"]
    stock_ids = stock_ids["comp"].str.split("　", expand=True)
    stock_ids.columns = ["id", "name"]
    stock_ids = stock_ids.id.unique().tolist()
    return stock_ids


def get_tax_id(stock_id):
    keep_dict = {}
    url = f"https://stock.wearn.com/abase.asp?kind={stock_id}"
    r = requests.get(url=url).content
    soup = BeautifulSoup(r, "html.parser")
    try:
        test = soup.find("table")
        keys, values = [item.text for item in soup.find_all("th")], [
            item.text for item in soup.find_all("td")
        ]
        res_dict = dict(zip(keys, values))
        for k, v in res_dict.items():
            if ("統一編號" in k) or ("主要經營業務" in k):
                keep_dict.update({k: v})
    except:
        print("failed")
    return keep_dict


if __name__ == "__main__":

    # Get All Stock ID
    data_rootpath = "data"
    listed_company_filepath = os.path.join(data_rootpath, "listed_company.csv")
    wearn_basicinfo_filepath = os.path.join(
        data_rootpath, "company_basicinfo_wearn.json"
    )
    stock_ids = getAllCompanies(filepath=listed_company_filepath)
    print(f"All stock id loaded: {len(stock_ids)}")

    try:
        with open(wearn_basicinfo_filepath, "r", encoding="utf-8") as f:
            collect_dict = json.load(f)
    except:
        collect_dict = {}

    for stock_id in tqdm(stock_ids):
        if not collect_dict.get(stock_id):
            keep_dict = get_tax_id(stock_id=stock_id)
            collect_dict.update({stock_id: keep_dict})
            time.sleep(1)

    with open(wearn_basicinfo_filepath, "w", encoding="utf-8") as f:
        json.dump(collect_dict, f, ensure_ascii=False, indent=4)
