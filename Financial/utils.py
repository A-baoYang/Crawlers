from bs4 import BeautifulSoup
import logging
import os
import pandas as pd
import requests
import re
import random
from tqdm import tqdm
import time


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
freeproxy_filepath = os.path.join(data_rootpath, "valid_ips.csv")
smartproxy_filepath = os.path.join(data_rootpath, "smartproxy_proxies.csv")
smartproxy_datacenter_filepath = os.path.join(
    data_rootpath, "smartproxy_test_datacenter_proxies.csv"
)
listed_company_filepath = os.path.join(
    data_rootpath, "Financial/data/twse_securities_ids.csv"
)


logger = logging.getLogger(__name__)


# Function
# initial logging
def init_logger(filename):
    logging.basicConfig(
        filename=filename,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
    )


# read company list
def getAllCompanies(filepath):
    stock_ids = pd.read_csv(filepath, header=None)
    stock_ids.columns = ["comp"]
    stock_ids = stock_ids["comp"].str.split("　", expand=True)
    stock_ids.columns = ["id", "name"]
    stock_ids = stock_ids.id.unique().tolist()
    return stock_ids


# get free ip for proxy
def getFreeIpProxy():
    free_proxy_url = "https://free-proxy-list.net/"
    res = requests.get(free_proxy_url, headers=headers)
    ip_list = re.findall("\d+\.\d+\.\d+\.\d+:\d+", res.text)
    return ip_list


# check if the ip is valid to use
def GetValidIpProxy(num_use):
    valid_ips = []
    check_ip_url = "https://api.ipify.org/?format=json"
    ip_list = getFreeIpProxy()

    for ip in tqdm(ip_list):
        try:
            res = requests.get(
                check_ip_url, proxies={"http": ip, "https": ip}, timeout=5
            )
            valid_ips.append(ip)
            print(res.json())
        except:
            print("Invalid: ", ip)

        if len(valid_ips) >= num_use:
            break

    return valid_ips


def changeUserAgentNProxy(
    maxtimes_changeIp,
    maxtimes_retry,
    url,
    method,
    payload,
    headers,
    user_agent_list,
    valid_ips,
):
    changedIp = 0
    success = 0
    start_time = time.time()

    while (changedIp < maxtimes_changeIp) and (success == 0):
        retry = 0
        timeout = 20
        headers["User-Agent"] = random.choice(user_agent_list)
        ip_proxy = random.choice(valid_ips)
        # ip_proxy = valid_ips[changedIp]

        while (retry < maxtimes_retry) and (success == 0):
            time.sleep(1)
            try:
                logger.info(f"{ip_proxy} Fetching {url} (timeout = {timeout})")
                if method == "get":
                    logger.info("Request Method = GET")
                    res = requests.get(
                        url,
                        headers=headers,
                        proxies={"http": ip_proxy, "https": ip_proxy},
                        timeout=timeout,
                    )
                else:
                    logger.info("Request Method = POST")
                    # print(payload)
                    res = requests.post(
                        url,
                        data=payload,
                        headers=headers,
                        proxies={"http": ip_proxy, "https": ip_proxy},
                        timeout=timeout,
                    )

                logger.info(f"crawled content length = {len(res.content)}")
                soup = BeautifulSoup(res.content, "html.parser")
                test = soup.find("table")
                success = 1
                logger.info("Success")
            except Exception as e:
                retry += 1
                timeout += 5
                logger.info(f"Error: {e}")
                logger.info(f"Retrying: {retry}")

        changedIp += 1

    one_req_time = time.time() - start_time
    logger.info(f"Time used = {one_req_time}")

    return res
