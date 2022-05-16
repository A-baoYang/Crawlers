#%%
from bs4 import BeautifulSoup
import datetime as dt
from dateutil.parser import parse as date_parse
import json
import logging
import numpy as np
import os
import pandas as pd
from qwikidata.sparql import return_sparql_query_results
import random
import requests
from tqdm import tqdm
import time
import urllib.parse

from utils import *

#%%
valid_ips = pd.read_csv(smartproxy_filepath).ip.values.tolist()
print(valid_ips)

#%%
maxtimes_changeIp = 5
maxtimes_retry = 3
headers["User-Agent"] = random.choice(user_agent_list)
#%%
# 蒐集所有產業 url
url = "https://ic.tpex.org.tw/index.php"
res = changeUserAgentNProxy(
    maxtimes_changeIp=maxtimes_changeIp,
    maxtimes_retry=maxtimes_retry,
    url=url,
    method="get",
    payload=None,
    headers=headers,
    user_agent_list=user_agent_list,
    valid_ips=valid_ips,
).content
soup = BeautifulSoup(res, "html.parser")
url_list = [
    "https://ic.tpex.org.tw/" + item["href"] 
    for item in soup.find("div", {"id": "example2"}).find_all("a", href=True) 
    if "introduce" in item["href"]
] + [
    "https://ic.tpex.org.tw/" + item["onclick"].replace("location.href=", "").replace("'","")
    for item in soup.find("div", {"id": "example2"}).find_all("span", {"class": "itemLink"}, onclick=True)
    if "introduce" in item["onclick"]
]
print(len(url_list))

ind_chain_comps = {}
ind_streams = {}
for url in tqdm(url_list):
    res = changeUserAgentNProxy(
        maxtimes_changeIp=maxtimes_changeIp,
        maxtimes_retry=maxtimes_retry,
        url=url,
        method="get",
        payload=None,
        headers=headers,
        user_agent_list=user_agent_list,
        valid_ips=valid_ips,
    ).content
    soup = BeautifulSoup(res, "html.parser")
    ind_name = soup.find("h3").text.replace("產業鏈簡介","")
    ind_stream = [
        [char for char in re.split("\n|\xa0", item.text) if char != ""]
        for item in soup.find_all("div", {"class", "chain"})
    ]
    ind_streams.update({ind_name: ind_stream})
    
    chain_items = soup.find_all("div", {"id": re.compile(".*companyList.*")})
    print([chain["title"] for chain in chain_items])
    chain_items = chain_items[:(len(chain_items)//2)]
    comp_in_chains = {}
    subchain_count = 0

    for chain in chain_items:
        chain_title = chain["title"]
        categories = len(chain.find_all("table"))

        if categories == 1:
            chain_comps = [
                chr for chr in 
                re.split("本國|外國|知名|\xa0", chain.find("table").text) 
                if "公司" not in chr and "企業" not in chr and chr != ""
            ]
        else:
            print(chain_title, subchain_count)
            chain_cate_names = [chr for chr in soup.find_all("div", {"class": "subchain-industry"})[subchain_count].text.split("\xa0") if "(" not in chr and chr != ""]
            chain_cate_comps = [item.text for item in soup.find_all("div", {"class": "subchain-company"})[subchain_count].find_all("table")]
            subchain_count += 1
            chain_comps = dict(zip(chain_cate_names, chain_cate_comps))
            for key, val in chain_comps.items():
                chain_comps[key] = [
                    chr for chr in re.split("本國|外國|知名|\xa0", val) 
                    if "公司" not in chr and "企業" not in chr and chr != ""
                ]

        comp_in_chains.update({chain_title: chain_comps})
    ind_chain_comps.update({ind_name: comp_in_chains})




# %%
new_ind_chain_comps = {}
for k in tqdm(ind_chain_comps):
    new_ind_chain_comps[k] = {}
    for stream_line in ind_streams[k]:
        new_ind_chain_comps[k].update({stream_line[0]: {}})
        for fid in range(len(stream_line[1:])):
            try:
                new_ind_chain_comps[k][stream_line[0]].update({stream_line[fid+1]: ind_chain_comps[k][stream_line[fid+1]]})
            except:
                field = list(ind_chain_comps[k].keys())[fid]
                new_ind_chain_comps[k][stream_line[0]].update({stream_line[fid+1]: ind_chain_comps[k][field]})

# %%
with open("ind_chain_comps.json", "w", encoding="utf-8") as f:
    json.dump(new_ind_chain_comps, f, ensure_ascii=False, indent=4)


# %%
