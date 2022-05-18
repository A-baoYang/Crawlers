from cgitb import html
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


def get_html_table(page_id):
    keep_dict = {}
    url = f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={page_id}"
    r = requests.get(url=url).text
    soup = BeautifulSoup(r, "html.parser")
    try:
        test = soup.find("table")
        title = soup.find("h2").text
        print(title)
        res = [
            [item.text for item in html_node.find_all("td")]
            for html_node in soup.find_all("tr")
        ]
    except:
        print("failed")
    return title, res


if __name__ == "__main__":
    
    user_agent_list = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    ]
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Sec-Gpc": "1",
        "Referer": "https://www.google.com/",
        "Dnt": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36",
    }
    data_rootpath = "../../forResearch/data/gcs/Crawling/"
    twse_securities_filepath = os.path.join(
        data_rootpath, "Financial/data/twse_securities_ids"
    )
    collect_dict = {}
    for page_id in tqdm(range(1, 13)):
        title, res = get_html_table(page_id=page_id)
        collect_dict.update(
            {
                page_id: {
                    "name": title,
                    "dataframe": res,
                }
            }
        )
        time.sleep(1)

    with open(twse_securities_filepath + ".json", "w", encoding="utf-8") as f:
        json.dump(collect_dict, f, ensure_ascii=False, indent=4)

    with pd.ExcelWriter(twse_securities_filepath + ".xlsx") as writer:
        for val in collect_dict.values():
            frame = val.get("dataframe")
            frame = pd.DataFrame(frame[1:], columns=frame[:1])
            frame.to_excel(writer, sheet_name=val.get("name"))
