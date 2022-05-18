from bs4 import BeautifulSoup
import datetime as dt
from dateutil.parser import parse as date_parse
import json
import logging
import numpy as np
import os
import pandas as pd
import random
import requests
from tqdm import tqdm
import time
import urllib.parse

from utils import *


logger = logging.getLogger(__name__)


def getArticleContent(
    source,
    url_list,
    headers,
    user_agent_list,
    valid_ips,
    maxtimes_changeIp,
    maxtimes_retry,
):
    headers["User-Agent"] = random.choice(user_agent_list)
    article_list = []
    for url in tqdm(url_list):
        try:
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
            # res = requests.get(url, headers=headers).content
            # logger.info(f"crawled content length = {len(res)}")
            # logger.info("Success")
            # logger.info(f"Time used = {(time.time() - start):.3f}")
            soup = BeautifulSoup(res, "html.parser")

            if source == "ltn":
                title = soup.find("h1").text
                article = soup.find("div", class_="text").text
                summary = soup.find("meta", {"name": "description"}).get("content")
                keywords = soup.find("meta", {"name": "news_keywords"}).get("content")
                publishdate = soup.find("meta", {"property": "pubdate"}).get("content")
            elif source == "moneydj":
                title = soup.find("h1").text
                article = soup.find("div", id="highlight").text
                summary = soup.find("meta", {"property": "description"}).get("content")
                keywords = soup.find("meta", {"property": "keywords"}).get("content")
                publishdate = soup.find("time").get("datetime")
            elif source == "moneyudn":
                title = soup.find("h1").text
                article = soup.find("section", id="article_body").text
                summary = soup.find("meta", {"name": "description"}).get("content")
                keywords = soup.find("meta", {"name": "news_keywords"}).get("content")
                publishdate = soup.find("meta", {"name": "date"}).get("content")
            elif source == "yahoofinance":
                title = soup.find("header", class_="caas-title-wrapper").find("h1").text
                article = soup.find("div", class_="caas-body").text
                summary = soup.find("meta", {"name": "description"}).get("content")
                keywords = soup.find("meta", {"name": "news_keywords"}).get("content")
                publishdate = soup.find("time").get("datetime")
            elif source == "cmoney":
                title = soup.find("h1").text
                article = soup.find("div", class_="rec-content").text
                summary = soup.find("meta", {"name": "description"}).get("content")
                keywords = soup.find("meta", {"property": "article:section"}).get(
                    "content"
                )
                publishdate = soup.find(
                    "meta", {"property": "article:published_time"}
                ).get("content")
            elif source == "technews":
                title = soup.find("h3", {"class": "post-title"}).text
                article = soup.find("div", {"class": "post-content"}).text.strip()
                article = "".join([item.strip() for item in re.split("\r|\n|\t|\xa0|\u3000", article) if item.strip()])
                summary = ""
                _preprocess = soup.find("h5", {"class": "date"}).text.strip()
                _preprocess = [item.strip() for item in re.split("\r|\n|\t", _preprocess) if item.strip()]
                keywords = _preprocess[-1].replace("Tagged: ", "")
                publishdate = date_parse(_preprocess[0]).strftime("%Y-%m-%dT%H:%M:%S")
            else:
                title = soup.find("h1").text if soup.find("h1") else ""
                article = soup.find("body").text if soup.find("body") else ""
                try:
                    summary = soup.find("meta", {"name": "description"}).get("content")
                except:
                    summary = ""
                try:
                    keywords = soup.find("meta", {"name": "news_keywords"}).get("content")
                except:
                    keywords = ""
                try:
                    publishdate = soup.find("meta", {"name": "date"}).get("content")
                except:
                    publishdate = ""

            article_list.append(
                (source, title, url, article, summary, keywords, publishdate)
            )

        except Exception as e:
            logger.info(f"Failed - {e}")

    return article_list


def getArticles(
    headers,
    user_agent_list,
    valid_ips,
    maxtimes_changeIp,
    maxtimes_retry,
    source,
    url_params,
):
    headers["User-Agent"] = random.choice(user_agent_list)
    url_list = []
    logger.info(f"Collecting urls from {source}: ")

    if source == "ltn":
        keyword, start_time, end_time, page_num = (
            url_params["keyword"],
            url_params["start_time"],
            url_params["end_time"],
            url_params["page_num"],
        )
        try:
            for i in tqdm(range(1, page_num + 1)):
                url = f"http://search.ltn.com.tw/list?keyword={keyword}&type=all&sort=date&start_time={start_time}&end_time={end_time}&page={i}"
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
                # res = requests.get(url, headers=headers).content
                # logger.info(f"crawled content length = {len(res)}")
                # logger.info("Success")
                # logger.info(f"Time used = {(time.time() - start):.3f}")
                soup = BeautifulSoup(res, "html.parser")
                try:
                    url_list += [
                        item.find("a", href=True)["href"]
                        for item in soup.find_all("ul")[3].find_all("li")
                    ]
                except:
                    break
        except:
            logger.info("Failed")

        logger.info(
            f"Getting article content from {source} urls: ({len(url_list)} urls)"
        )
        article_list = getArticleContent(
            source,
            url_list,
            headers,
            user_agent_list,
            valid_ips,
            maxtimes_changeIp,
            maxtimes_retry,
        )

    elif source == "cnyes":
        start_time = dt.datetime.strptime(url_params["start_time"], "%Y%m%d").strftime(
            "%s"
        )
        end_time = dt.datetime.strptime(url_params["end_time"], "%Y%m%d").strftime("%s")
        print(start_time, end_time)
        base_url = f"https://api.cnyes.com/media/api/v1/newslist/category/tw_stock?startAt={start_time}&endAt={end_time}&limit=100"
        page_num = requests.get(url=base_url).json()["items"]["last_page"]
        try:
            article_list = []
            for i in tqdm(range(1, page_num + 1)):
                url = base_url + f"&page={i}"
                res = changeUserAgentNProxy(
                    maxtimes_changeIp=maxtimes_changeIp,
                    maxtimes_retry=maxtimes_retry,
                    url=url,
                    method="get",
                    payload=None,
                    headers=headers,
                    user_agent_list=user_agent_list,
                    valid_ips=valid_ips,
                ).json()
                article_list += [
                    (
                        source,
                        item["title"],
                        item["content"],
                        item["summary"],
                        item["categoryName"],
                        dt.datetime.fromtimestamp(item["publishAt"]).strftime(
                            "%Y/%m/%d %H:%M:%S"
                        ),
                        item["stock"],
                    )
                    for item in res["items"]["data"]
                ]
                logger.info(f"{source} - total urls: {len(article_list)}")
        except:
            logger.info(f"Failed at {source} - page{i}")

    elif source == "moneydj":
        keyword, start_time, end_time, page_num = (
            url_params["keyword"],
            url_params["start_time"],
            url_params["end_time"],
            url_params["page_num"],
        )
        try:
            for i in tqdm(range(0, page_num)):
                url = f"https://www.moneydj.com/KMDJ/search/list.aspx?index1={i}&_Query_={keyword}&_QueryType_=NW&last={start_time}&end={end_time}&count=300"
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
                try:
                    url_list += [
                        "https://www.moneydj.com/KMDJ/" + item["href"].split("../")[-1]
                        for item in soup.find(
                            "table", id="MainContent_Contents_data_gv"
                        ).find_all("a", href=True)
                    ]
                except:
                    break
        except:
            logger.info("Failed")

        logger.info(
            f"Getting article content from {source} urls: ({len(url_list)} urls)"
        )
        article_list = getArticleContent(
            source,
            url_list,
            headers,
            user_agent_list,
            valid_ips,
            maxtimes_changeIp,
            maxtimes_retry,
        )

    elif source == "moneyudn":
        # 無法指定時間抓取歷史文章紀錄
        page_num = url_params["page_num"]
        try:
            for i in tqdm(range(1, page_num + 1)):
                url = f"https://money.udn.com/rank/newest/1001/0/{i}"
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
                try:
                    url_list += [
                        item.find("a", href=True)["href"]
                        for item in soup.find_all("li", class_="story-headline-wrapper")
                    ]
                except:
                    break
        except:
            logger.info("Failed")

        logger.info(
            f"Getting article content from {source} urls: ({len(url_list)} urls)"
        )
        article_list = getArticleContent(
            source,
            url_list,
            headers,
            user_agent_list,
            valid_ips,
            maxtimes_changeIp,
            maxtimes_retry,
        )

    elif source == "yahoofinance":
        # 無法指定時間抓取歷史文章紀錄
        url_list = []
        try:
            for url in [
                "https://tw.stock.yahoo.com/rss?category=column",
                "https://tw.stock.yahoo.com/rss?category=tw-market",
                "https://tw.stock.yahoo.com/rss?category=intl-markets",
                "https://tw.stock.yahoo.com/rss?category=funds-news",
                "https://tw.stock.yahoo.com/rss?category=research",
                "https://tw.stock.yahoo.com/rss?category=personal-finance",
            ]:
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
                try:
                    url_list += [
                        "https" + re.split("https|html", item.text)[1] + "html"
                        for item in soup.find_all("item")
                    ]
                    logger.info(f"{source}-{url} has {len(url_list)} urls")
                except:
                    break
        except:
            logger.info("Failed")

        logger.info(
            f"Getting article content from {source} urls: ({len(url_list)} urls)"
        )
        article_list = getArticleContent(
            source,
            url_list,
            headers,
            user_agent_list,
            valid_ips,
            maxtimes_changeIp,
            maxtimes_retry,
        )

    elif source == "cmoney":
        # 無法指定時間抓取歷史文章紀錄
        page_num = url_params["page_num"]
        try:
            for i in tqdm(range(1, page_num + 1)):
                url = f"https://www.cmoney.tw/notes/?bid=22814&p={i}"
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
                try:
                    url_list += [
                        "https://www.cmoney.tw"
                        + item.find("h2").find("a", href=True)["href"]
                        for item in soup.find_all("div", class_="p-article")
                    ]
                    logger.info(f"{source}-{url} has {len(url_list)} urls")
                except:
                    break
        except:
            logger.info("Failed")

        logger.info(
            f"Getting article content from {source} urls: ({len(url_list)} urls)"
        )
        article_list = getArticleContent(
            source,
            url_list,
            headers,
            user_agent_list,
            valid_ips,
            maxtimes_changeIp,
            maxtimes_retry,
        )

    elif source == "technews":
        keyword, page_num = (
            url_params["keyword"], 
            url_params["page_num"]
        )
        try:
            for i in tqdm(range(0, page_num)):
                # 出現阻檔問題
                url = f"https://cse.google.com/cse/element/v1?rsz=filtered_cse&num=10&hl=zh-TW&source=gcsc&gss=.tw&cselibv=3e1664f444e6eb06&cx=006691780243297298869:qzwcjldsbsm&q={keyword}&safe=off&cse_tok=AJvRUv2MvUedxLV4ukS90Suuk6VK:1649838617138&filter=0&sort=&exp=csqr,cc&callback=google.search.cse.api18660"
                # url = "https://cse.google.com/cse/element/v1"
                # crawling_url_params = {
                #     "rsz": "filtered_cse", 
                #     "num": "20",  # at most
                #     "hl": "zh-TW", 
                #     "source": "gcsc", 
                #     "gss": ".tw", 
                #     "start": "i * 10", 
                #     "cselibv": "3e1664f444e6eb06", 
                #     "cx": "006691780243297298869:qzwcjldsbsm", 
                #     "q": keyword, 
                #     "safe": "off", 
                #     "cse_tok": "AJvRUv3ULP0axgVbRj5XKNcu0gZ8:1649755520369", 
                #     "filter": "0", 
                #     "sort": "", 
                #     "exp": "csqr,cc", 
                #     "rsToken": "undefined", 
                #     "afsExperimentId": "undefined", 
                #     "callback": "google.search.cse.api17164",
                # }
                # prepReq = requests.PreparedRequest()
                # prepReq.prepare_url(url, crawling_url_params)
                # url = prepReq.url
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
                logger.info(soup.text[:100])
                start_idx = len(soup.text.split("(")[0]) + 1
                print(json.loads(soup.text[start_idx:-2])["results"][0].keys())
                url_list += [
                    item["unescapedUrl"] for item in 
                    json.loads(soup.text[start_idx:-2])["results"]
                ]
                logger.info(f"{source}-{url} has {len(url_list)} urls")
        except:
            logger.info("Failed")

        logger.info(
            f"Getting article content from {source} urls: ({len(url_list)} urls)"
        )
        article_list = getArticleContent(
            source,
            url_list,
            headers,
            user_agent_list,
            valid_ips,
            maxtimes_changeIp,
            maxtimes_retry,
        )


    elif source == "google":
        keyword, start_time, end_time, page_num = (
            urllib.parse.quote(url_params["keyword"]),
            dt.datetime.strptime(url_params["start_time"]).strftime("%m/%d/%Y"),
            dt.datetime.strptime(url_params["end_time"]).strftime("%m/%d/%Y"),
            url_params["page_num"],
        )
        try:
            for i in tqdm(range(0, page_num)):
                url = f"https://www.google.com/search?q={keyword}&tbs=cdr:1,cd_min:{start_time},cd_max:{end_time}&tbm=nws&sxsrf=APq-WBssZJ7PXT95uFzRjG5wLh-pJpqZuA:1649747697179&ei=8SZVYr3VCpCb-AbJy4iIBg&start={i*10}&sa=N&ved=2ahUKEwj9kdaL_Y33AhWQDd4KHcklAmEQ8tMDegQIARA-&biw=1440&bih=631&dpr=1"
                res = changeUserAgentNProxy(
                    maxtimes_changeIp=maxtimes_changeIp,
                    maxtimes_retry=maxtimes_retry,
                    url=url,
                    method="get",
                    payload=None,
                    headers=headers,
                    user_agent_list=user_agent_list,
                    valid_ips=valid_ips,
                ).json()
                # soup = BeautifulSoup(res, "html.parser")
                try:
                    url_list += [
                        item.find("a", href=True)["href"]
                        for item in soup.find_all("g-card")
                    ]
                except:
                    break
        except:
            logger.info("Failed")

        logger.info(
            f"Getting article content from {source} urls: ({len(url_list)} urls)"
        )
        url_domain = urllib.parse.urlparse(source).netloc
        article_list = getArticleContent(
            url_domain,
            url_list,
            headers,
            user_agent_list,
            valid_ips,
            maxtimes_changeIp,
            maxtimes_retry,
        )

    else:
        article_list = []

    return article_list


def store_data(data, output_filepath):
    with open(
        os.path.join(output_filepath),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Main
init_logger()
starttime = time.time()
start_date = "20220101"
end_date = "20220413"
keyword = "俄烏戰爭"
output_dir = os.path.join(data_rootpath, "Financial/data/taiwan_financial_news")
output_filepath = os.path.join(output_dir, f"addon-news-{start_date}_{end_date}-{keyword}.json")
print(output_filepath)
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
valid_ips = pd.read_csv(smartproxy_filepath).ip.values.tolist() # smartproxy_filepath, freeproxy_filepath
# logger.info(f"{valid_ips}")

# Set media crawler params
maxtimes_changeIp = 5
maxtimes_retry = 3
month_article_list = dict()
media_list = ["ltn","moneydj"]
url_params = {
    "ltn": {
        "keyword": "俄烏戰爭",
        "start_time": start_date,
        "end_time": end_date,
        "page_num": 500,
    },
    "cnyes": {"start_time": start_date, "end_time": end_date},
    "moneydj": {
        "keyword": "俄烏戰爭",
        "start_time": "2022/01/01",
        "end_time": "2022/04/13",
        "page_num": 500,
    },
    "moneyudn": {"page_num": 5},
    "yahoofinance": {},
    "cmoney": {"page_num": 5},
    "technews": {
        "keyword": "俄烏戰爭",
        "page_num": 100,
    }
}

article_dict = dict()
for media in tqdm(media_list):
    articles_list = getArticles(
        headers=headers,
        user_agent_list=user_agent_list,
        valid_ips=valid_ips,
        maxtimes_changeIp=maxtimes_changeIp,
        maxtimes_retry=maxtimes_retry,
        url_params=url_params[media],
        source=media,
    )
    if article_dict.get(media):
        print(article_dict.keys())
        article_dict[media] += articles_list
    else:
        article_dict.update({media: articles_list})

    store_data(data=article_dict, output_filepath=output_filepath)
