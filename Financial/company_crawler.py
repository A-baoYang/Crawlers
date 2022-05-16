from bs4 import BeautifulSoup
import datetime as dt
import json
import logging
import numpy as np
import os
import pandas as pd
import random
from tqdm import tqdm
import time
import urllib.parse

from utils import *

logger = logging.getLogger(__name__)


def getStockCates(idx, headers, user_agent_list, valid_ips):

    market_categories = ["上市", "上櫃", "興櫃", "電子產業", "概念股", "集團股"]
    market_cat = market_categories[idx]
    url = f"https://goodinfo.tw/StockInfo/StockList.asp?MARKET_CAT={market_cat}"

    res = changeUserAgentNProxy(url, headers, user_agent_list, valid_ips).content
    soup = BeautifulSoup(res, "html.parser")

    list_stock_cate = soup.find("table", {"id": f"MENU{idx+2}"}).find_all(
        "td", {"colspan": "4"}
    )
    list_stock_cate = [
        str(item).split(f"{market_cat}_")[-1].split("@*=")[0]
        for item in list_stock_cate
    ]
    list_stock_cate = [
        item.replace('="" colspan="4"', "") if "colspan" in item else item
        for item in list_stock_cate
        if (len(item) > 0) and (market_cat not in item) and ("<td" not in item)
    ]
    return list_stock_cate


def getCateStockList(market_cat, ind, headers, user_agent_list, valid_ips):

    url = f"https://goodinfo.tw/StockInfo/StockList.asp?MARKET_CAT={market_cat}&INDUSTRY_CAT={ind}"

    res = changeUserAgentNProxy(url, headers, user_agent_list, valid_ips).content
    soup = BeautifulSoup(res, "html.parser")

    list_stock = [
        item.text
        for item in soup.find("table", {"class": "r10_0_0_10 b1 p4_1"}).find_all("td")
    ]
    list_stock = [
        (x, y) for x, y in zip(list_stock[::2], list_stock[1::2]) if x != "代號"
    ]
    return list_stock


def getStockBasicinfo(
    source,
    stock_id,
    headers,
    user_agent_list,
    valid_ips,
    maxtimes_changeIp,
    maxtimes_retry,
):

    if source == "goodinfo":
        url = f"https://goodinfo.tw/tw/BasicInfo.asp?STOCK_ID={stock_id}"
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

        keys = [
            item.text
            for item in soup.find("table", {"class": "b1 p4_6 r10"}).find_all(
                "td", {"class": "bg_h1"}
            )
        ]
        values = [
            item.text.replace("\xa0", "")
            for item in soup.find("table", {"class": "b1 p4_6 r10"}).find_all(
                "td", {"bgcolor": "white"}
            )
        ]

        try:
            childCompany_headers = [
                item.text
                for item in soup.find(
                    "table", {"class": "b1 p4_6 r10 row_bg_2n row_mouse_over"}
                )
                .find("tr", {"class": "bg_h1"})
                .find_all("th")
            ]
            childCompany_rows = [
                [i.text for i in item.find_all("td")]
                for item in soup.find(
                    "table", {"class": "b1 p4_6 r10 row_bg_2n row_mouse_over"}
                ).find_all("tr", {"align": "left"})
            ]
        except:
            childCompany_headers = []
            childCompany_rows = []

        return_value = (keys, values, childCompany_headers, childCompany_rows)

    elif source == "moneydj":
        url = f"https://concords.moneydj.com/z/zc/zca/zca.djhtm?a={stock_id}"
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
        keys = [item.text for item in soup.find_all("td", {"class": "t4t1"})]
        idx_1 = keys.index("公司地址")
        idx_2 = keys.index("公積配股")
        keys = keys[: idx_1 + 1]
        values_n1 = [item.text for item in soup.find_all("td", {"class": "t3n1"})]
        values_n1 = values_n1[: idx_2 + 1]
        values_t1 = [item.text for item in soup.find_all("td", {"class": "t3t1"})]
        values_t1 = [item for item in values_t1 if item != "\xa0"][:7]
        values = values_n1 + values_t1

        return_value = [keys, values]

    return return_value


def getStockNews(
    stock_id, headers, user_agent_list, valid_ips, maxtimes_changeIp, maxtimes_retry
):

    url = f"https://goodinfo.tw/tw/StockAnnounceList.asp?PAGE=1&START_DT=2021%2F09%2F12&END_DT=2021%2F12%2F12&STOCK_ID={stock_id}&KEY_WORD=&NEWS_SRC=%E5%85%AC%E5%91%8A%E8%A8%8A%E6%81%AF&NEWS_SRC=Anue%E9%89%85%E4%BA%A8&NEWS_SRC=ETtoday%E6%96%B0%E8%81%9E%E9%9B%B2&NEWS_SRC=PR+Newswire"
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
    news_list = [
        [
            item.find_all("td")[0].text,
            item.find_all("td")[1].text,
            urllib.parse.unquote(
                item.find_all("td")[1]
                .find("a")
                .get("href")
                .replace("OpenLink.asp?LINK=", "")
                .split("%3Futm%5Fsource")[0]
            ),
        ]
        for item in soup.find(
            "table", {"class": "p4_4 row_bg_2n row_mouse_over"}
        ).find_all("tr")
    ]

    return news_list


def getShareHoldings(
    stock_id,
    year,
    month,
    headers,
    user_agent_list,
    valid_ips,
    maxtimes_changeIp,
    maxtimes_retry,
):

    url = "https://mops.twse.com.tw/mops/web/ajax_stapap1"
    headers.update({"Content-Type": "application/x-www-form-urlencoded"})
    payload = {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "keyword4": "",
        "code1": "",
        "TYPEK2": "",
        "checkbtn": "",
        "queryName": "co_id",
        "inpuType": "co_id",
        "TYPEK": "all",
        "isnew": "true",
        "co_id": str(stock_id),
        "year": str(year),
        "month": str(month).zfill(2),
    }
    today = dt.datetime.today()
    if (year == today.year - 1911) and (
        (month == today.month) or (month == today.month - 1)
    ):
        payload["isnew"] = "true"
    else:
        payload["isnew"] = "false"

    res = changeUserAgentNProxy(
        maxtimes_changeIp=maxtimes_changeIp,
        maxtimes_retry=maxtimes_retry,
        url=url,
        method="post",
        payload=payload,
        headers=headers,
        user_agent_list=user_agent_list,
        valid_ips=valid_ips,
    ).content
    soup = BeautifulSoup(res, "html.parser")

    shareholdings_records = [
        [i.text.strip() for i in item.find_all("td")]
        for item in soup.find("table", {"class": "hasBorder"}).find_all("tr")
    ]

    return shareholdings_records


def store_data(data_dict):

    with open(
        os.path.join(
            data_rootpath, "Financial/data/company_basicinfo_all_securities.json"
        ),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(data_dict["company_basicinfo"], f, ensure_ascii=False, indent=4)

    # with open(os.path.join(data_rootpath, 'Financial/data/company_shareholdings.json'), 'w', encoding='utf-8') as f:
    #     json.dump(data_dict["company_shareholdings"], f, ensure_ascii=False, indent=4)

    # with open(os.path.join(data_rootpath, 'Financial/data/company_news.json'), 'w', encoding='utf-8') as f:
    #     json.dump(data_dict["company_news"], f, ensure_ascii=False, indent=4)

    # store invalid ids for re-crawling
    inv_dict = {
        "InvalidIDs_company_basic_info_goodinfo": data_dict[
            "basicinfo_goodinfo_invalidIds"
        ],
        "InvalidIDs_company_basic_info_moneydj": data_dict[
            "basicinfo_moneydj_invalidIds"
        ],
        # "InvalidIDs_company_share_holdings": data_dict["shareholdings_invalidIds"],
        # "InvalidIDs_company_news": data_dict["news_invalidIds"]
    }
    with open(
        os.path.join(data_rootpath, "Financial/data/invalid_stockIDs.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(inv_dict, f, ensure_ascii=False, indent=4)


# Main
init_logger()
starttime = time.time()
# Get Free Valid IP
# valid_ips = GetValidIpProxy(num_use=10)
# valid_ips = pd.read_csv(smartproxy_filepath).ip.values.tolist()
valid_ips = pd.read_csv(smartproxy_datacenter_filepath).ip.values.tolist()
logger.info(f"{valid_ips}")
# df_validIp = pd.DataFrame({"ip": valid_ips})
# df_validIp.to_csv(os.path.join(data_rootpath, "Financial/data/valid_ips.csv"), index=False)


# Get All Stock ID
# stock_ids = getAllCompanies(filepath=listed_company_filepath)
stock_ids = pd.read_csv(listed_company_filepath).id.values.tolist()
logger.info(f"Total stocks: {len(stock_ids)}")
company_basicinfo = dict()
# company_shareholdings = dict()
# company_news = dict()
basicinfo_goodinfo_invalidIds = list()
basicinfo_moneydj_invalidIds = list()
# shareholdings_invalidIds = list()
# news_invalidIds = list()
maxtimes_changeIp = 5
maxtimes_retry = 3

for stock_id in tqdm(stock_ids):

    # company basic - moneydj
    try:
        [keys, values] = getStockBasicinfo(
            source="moneydj",
            stock_id=stock_id,
            headers=headers,
            user_agent_list=user_agent_list,
            valid_ips=valid_ips,
            maxtimes_changeIp=maxtimes_changeIp,
            maxtimes_retry=maxtimes_retry,
        )
        stock_basicinfo = dict(zip(keys, values))
        company_basicinfo.update({stock_id: stock_basicinfo})
    except Exception as e:
        print(e)
        company_basicinfo.update({stock_id: dict()})
        basicinfo_moneydj_invalidIds.append(stock_id)

    # company basic - goodinfo
    try:
        [keys, values, childCompany_headers, childCompany_rows] = getStockBasicinfo(
            source="goodinfo",
            stock_id=stock_id,
            headers=headers,
            user_agent_list=user_agent_list,
            valid_ips=valid_ips,
            maxtimes_changeIp=maxtimes_changeIp,
            maxtimes_retry=maxtimes_retry,
        )
        childCompany_rows = np.array(childCompany_rows)
        if len(keys) != len(values):
            basicinfo_goodinfo_invalidIds.append(stock_id)
        else:
            _dict = dict(zip(keys, values))
            # merge specific key-value into moneydj basic info
            select_col = (
                ["股票代號", "股票名稱", "產業別", "上市/上櫃", "公司名稱", "英文簡稱", "統一編號"]
                if stock_id not in basicinfo_moneydj_invalidIds
                else list(_dict.keys())
            )

            for col in select_col:
                company_basicinfo[stock_id].update({col: _dict[col]})
    except Exception as e:
        logger.info(f"{e}")
        basicinfo_goodinfo_invalidIds.append(stock_id)

    try:
        # child companies
        childcomps = list()
        if len(childCompany_headers) == 0:
            company_basicinfo[stock_id].update({"重要子公司": childcomps})
        elif (len(childCompany_headers) != 4) or (childCompany_rows.shape[1] != 4):
            basicinfo_goodinfo_invalidIds.append(stock_id)
        else:
            for i in range(len(childCompany_rows)):
                childcomps.append(dict(zip(childCompany_headers, childCompany_rows[i])))
            company_basicinfo[stock_id].update({"重要子公司": childcomps})
    except Exception as e:
        logger.info(f"{e}")
        basicinfo_goodinfo_invalidIds.append(stock_id)

    # # share holdings
    # try:
    #     shareholdings_records = getShareHoldings(stock_id=stock_id, year=110, month=12, headers=headers,
    #                             user_agent_list=user_agent_list, valid_ips=valid_ips, maxtimes_changeIp=5, maxtimes_retry=3)
    #     company_shareholdings.update({stock_id: shareholdings_records})
    # except Exception as e:
    #     print(e)
    #     shareholdings_invalidIds.append(stock_id)

    # # company news
    # try:
    #     news_list = getStockNews(stock_id=stock_id, headers=headers, user_agent_list=user_agent_list, valid_ips=valid_ips, maxtimes_changeIp=5, maxtimes_retry=3)
    #     company_news.update({stock_id: news_list})
    # except Exception as e:
    #     print(e)
    #     news_invalidIds.append(stock_id)

    # 每 500 間公司爬完就存一次
    if (stock_ids.index(stock_id) + 1) % 10 == 0:
        data_dict = {
            # "month_article_list": month_article_list,
            "company_basicinfo": company_basicinfo,
            # "company_shareholdings": company_shareholdings,
            # "company_news": company_news,
            "basicinfo_goodinfo_invalidIds": basicinfo_goodinfo_invalidIds,
            "basicinfo_moneydj_invalidIds": basicinfo_moneydj_invalidIds,
            # "shareholdings_invalidIds": shareholdings_invalidIds,
            # "news_invalidIds": news_invalidIds,
        }

        store_data(data_dict=data_dict)
        logger.info(
            f">> Data stored at {stock_ids.index(stock_id)} stock_id: {stock_id}"
        )

# try:
#     print(len(company_shareholdings.keys()), company_shareholdings.keys())
#     print(len(company_news.keys()), company_news.keys())
# except:
#     print('error ')

logger.info(f"Total Used Time = {(time.time() - starttime):.3f}")
