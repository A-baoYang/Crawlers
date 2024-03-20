import arrow
from bs4 import BeautifulSoup
import json
import os
import requests
import re
from time import sleep
import numpy as np
from tqdm import tqdm
from urllib.parse import urlparse


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
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
}
weird_encoding_domains = [
    "www.kmuh.org.tw",
    "xz.people.com.cn",
    "wlshosp.org.tw",
    "www.ccd.mohw.gov.tw",
    "www.chp.gov.hk",
    "wwwv.tsgh.ndmctsgh.edu.tw",
    "www.nant.mohw.gov.tw",
    "www.elderly.gov.hk",
    "www.tmuh.org.tw",
    "www.sph.org.tw",
    "wd.vghtpe.gov.tw",
    "www.kmsh.gov.tw",
    "lxjk.people.cn",
    "epaper.ntuh.gov.tw",
    "www.health.ntpc.gov.tw",
    "www.vghtc.gov.tw",
    "web1.fyh.mohw.gov.tw",
    "www.hospital.fju.edu.tw",
    "www.kgh.com.tw",
    "sp1.hso.mohw.gov.tw",
    "www.tmuh.org.tw",
]
# ip_proxyies = [
#     f"http://user-abaoyang:abaotest@gate.dc.smartproxy.com:2000{i}"
#     for i in list(range(1, 10))
# ]
all_keyword_filepath = "test-3high_gsrp_keywords.json"
article_output_filepath = "test-3high_gsrp_articles.json"


def fetch_gsrp(kw=None, url=None):
    """固定用來抓取 Google 搜尋結果頁及其他網頁內容"""
    if not url:
        url = f"https://www.google.com/search?q={kw}&oq={kw}&aqs=chrome..69i57j69i65.5309j0j1&sourceid=chrome&ie=UTF-8"
    print(url)
    sleep(0.5)
    r = requests.get(
        url,
        headers=headers,
        # proxies={
        #     "http": random.choice(ip_proxyies),
        #     "https": random.choice(ip_proxyies),
        # },
    )
    # 特定網域會產生亂碼，需先修改編碼再取出 text - https://sjkou.net/2017/01/06/python-requests-encoding/
    if urlparse(url).netloc in weird_encoding_domains:
        r.encoding = "big5"
    r = r.text
    soup = BeautifulSoup(r, "html.parser")
    return soup


def store_data(data, filename):
    output_filepath = os.path.join(os.getcwd(), filename)
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data has stored at {output_filepath}.")


related_keywords = {}
# article_results = {}
# starting_keywords = ["高血壓", "高血脂", "高血糖"]
starting_keywords = ["海芙音波"]
starting_kw = "比特幣"
starting_keywords = [starting_kw]
# starting_keywords = ["生成式AI"]


def get_related_kw_from_gsrp(lv1_kw, layer_num):
    soup = fetch_gsrp(kw=lv1_kw)
    start = soup.find("div", text = re.compile('相關搜尋'))
    collect_kws = []
    while start and start.find_next("a"):
        start = start.find_next("a")
        if start.text and start.text not in ['更多結果', '再試一次', '影片', '圖片', '新聞', '地圖', '更多']:
            collect_kws.append((start.text, layer_num))
    
    return collect_kws


def run_keyword_fetch(starting_keywords, layer_num):
    # 要獲取的關鍵字層數
    origin_layer_num = layer_num
    while True:
        for lv1_kw in tqdm(starting_keywords):
            collect_kws = get_related_kw_from_gsrp(
                lv1_kw, layer_num=origin_layer_num - layer_num + 1)
            # related_keywords.append({lv1_kw: collect_kws, "layer": origin_layer_num - layer_num + 1})
            related_keywords.update({lv1_kw: collect_kws})
        layer_num -= 1
        if layer_num == 0:
            break
        else:
            starting_keywords = np.unique(
                [
                    lv2_kw[0] for lv1_kw in related_keywords.keys() 
                    for lv2_kw in related_keywords[lv1_kw] 
                    if lv2_kw[0] not in related_keywords
                    and len(lv2_kw[0]) >= len(lv1_kw)
                ]
            )

    currdt = arrow.now().format("YYYYMMDDTHHmmss")
    store_data(data=related_keywords, filename=f"gsrp_keywords-{currdt}.json")
    return related_keywords


# for lv1_kw in tqdm(starting_keywords):
#     collect_kws = get_related_kw_from_gsrp(lv1_kw)
#     related_keywords.update({lv1_kw: collect_kws})
#     for lv2_kw in collect_kws:
#         collect_kws = get_related_kw_from_gsrp(lv2_kw)
#         related_keywords.update({lv2_kw: collect_kws})
#         for lv3_kw in collect_kws:
#             collect_kws = get_related_kw_from_gsrp(lv3_kw)
#             related_keywords.update({lv3_kw: collect_kws})

# store_data(data=related_keywords, filename="3high_gsrp_keywords_lv1.json")

# for i in range(2, 11):
#     ref_dict = related_keywords.copy()
#     related_keywords = {}
#     for lv1_kw in tqdm(ref_dict.keys()):
#         if ref_dict[lv1_kw]:
#             for lv2_kw in tqdm(ref_dict[lv1_kw]):
#                 soup = fetch_gsrp(kw=lv2_kw)
#                 try:
#                     lv3_kws = [
#                         item.text
#                         for item in soup.find_all("a", id=target_div_id)
#                     ]
#                 except Exception as e:
#                     lv3_kws = []
#                     print(e)
#                     pass
#                 finally:
#                     related_keywords.update({lv2_kw: lv3_kws})
#         else:
#             pass

#     store_data(data=related_keywords, filename=f"3high_gsrp_keywords_lv{i}.json")


