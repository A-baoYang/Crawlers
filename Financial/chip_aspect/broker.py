import logging
import os
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm


class Crawler(object):
    def __init__(self, log_name):
        self.log_name = log_name
        self.headers = {
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
        self.user_agent_list = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        ]
        self.data_positions = get_data_positions()
        smartproxy_filepath = os.path.join(self.data_positions["home_dir"], "forResearch/data/gcs/Crawling/", "smartproxy_proxies.csv")
        self.valid_ips = pd.read_csv(smartproxy_filepath)["ip"].values.tolist()

    def init_logger(self) -> None:
        logging.basicConfig(
            filename=f"{self.log_name}.log",
            filemode="w",
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%m/%d/%Y %H:%M:%S",
            level=logging.INFO,
        )
        
    def changeUserAgentNProxy(
        self,
        maxtimes_changeIp,
        maxtimes_retry,
        url,
        method,
        payload
    ):
        
        import random
        import requests

        self.logger = logging.getLogger(__name__)
        self.init_logger()
        changedIp = 0
        success = 0
        start_time = time.time()

        while (changedIp < maxtimes_changeIp) and (success == 0):
            retry = 0
            timeout = 20
            self.headers["User-Agent"] = random.choice(self.user_agent_list)
            ip_proxy = random.choice(self.valid_ips)

            while (retry < maxtimes_retry) and (success == 0):
                time.sleep(1)
                try:
                    self.logger.info(f"{ip_proxy} Fetching {url} (timeout = {timeout})")
                    if method == "get":
                        self.logger.info("Request Method = GET")
                        res = requests.get(
                            url,
                            headers=self.headers,
                            proxies={"http": ip_proxy, "https": ip_proxy},
                            timeout=timeout,
                        )
                    else:
                        self.logger.info("Request Method = POST")
                        # print(payload)
                        res = requests.post(
                            url,
                            data=payload,
                            headers=self.headers,
                            proxies={"http": ip_proxy, "https": ip_proxy},
                            timeout=timeout,
                        )
                    self.logger.info(f"crawled content length = {len(res.content)}")
                    soup = BeautifulSoup(res.content, "html.parser")
                    test = soup.find("table")
                    success = 1

                except Exception as e:
                    retry += 1
                    timeout += 5
                    self.logger.info(f"Error: {e}")
                    self.logger.info(f"Retrying: {retry}")

            changedIp += 1

        one_req_time = time.time() - start_time
        self.logger.info(f"Time used = {one_req_time}")
        return res

    def get_tw_industry_index(self, start_year, start_month, end_year, end_month, headers):

        import datetime as dt
        import requests

        self.headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
        self.headers["Referer"] = "https://www.tpex.org.tw/web/stock/aftertrading/all_daily_index/sectinx.php?l=zh-tw"

        def month_year_iter(start_year, start_month, end_year, end_month):
            start_ym = 12 * start_year + start_month - 1
            end_ym = 12 * end_year + end_month - 1
            for ym in range(start_ym, end_ym):
                y, m = divmod(ym, 12)
                yield y, m + 1

        data_list = []
        for d in tqdm(month_year_iter(start_year, start_month, end_year, end_month)):
            time.sleep(1)
            d_0 = d[0] - 1911 if d[0] > 1911 else d[0]
            d_1 = str(d[1]).zfill(2)

            url = f"https://www.tpex.org.tw/web/stock/aftertrading/index_monthly/idxsm_result.php?l=zh-tw&d={d_0}/{d_1}"
            try:
                res = self.changeUserAgentNProxy(
                        maxtimes_changeIp=5,
                        maxtimes_retry=3,
                        url=url,
                        method="get",
                        payload=None
                    )
                # res = requests.get(url=url, headers=headers)
                res.encoding = "utf-8-sig"
                res_json = res.json()
                if res_json["aaData"]:
                    data_list += res_json["aaData"]
            except Exception as e:
                print(f"Error at {url}: \n{e}")
                pass
        
        ind_names = [
            "紡織纖維", "電機機械", "鋼鐵工業", "電子工業", "建材營造", "航運業", 
            "觀光事業", "其他", "化學工業", "生技醫療", "半導體業", "電腦及週邊設備業", 
            "光電業", "通信網路業", "電子零組件業", "電子通路業", "資訊服務業", 
            "其他電子業", "文化創意業", "線上遊戲業"
        ]
        df = pd.DataFrame(data_list, columns=["Date"] + ind_names)
        return df

    def get_broker_hold(self, stock_id=2330, start_date="2022-4-11", end_date="2022-4-15"):
        """ 富邦證券法人持股明細 """

        # 檢查歷史紀錄有無存過
        self.broker_hold_filepath = os.path.join(
            self.data_positions["chip_aspect"], 
            f"brokerhold_{stock_id}_{start_date}_{end_date}.csv"
        )
        if not os.path.exists(self.broker_hold_filepath):

            self.headers["Content-Type"] = "text/html;Charset=big5"
            url = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcl/zcl.djhtm?a={stock_id}&c={start_date}&d={end_date}"
            res = self.changeUserAgentNProxy(
                maxtimes_changeIp=5,
                maxtimes_retry=3,
                url=url,
                method="get",
                payload=None
            )
            res.encoding = "big5"
            soup = BeautifulSoup(res.content, "html.parser")
            startpoint = len(soup.find_all("tr", {"id": "oScrollHead"})) + len(soup.find_all("tr", {"id": "oScrollMenu"}))
            table = soup.find("table", {"class": "t01"}).find_all("tr")[startpoint:-1]
            table = [[td.text for td in tr.find_all("td")] for tr in table]
            df = pd.DataFrame(
                table, 
                columns=[
                    "日期","買賣超-外資","買賣超-投信","買賣超-自營商","買賣超-單日合計",
                    "估計持股-外資","估計持股-投信","估計持股-自營商","估計持股-單日合計",
                    "持股比重-外資","持股比重-三大法人合計"]
                )
            df["日期"] = df["日期"].apply(lambda x: chinese_foreign_date_convert(date_str=x, target="foreign", splitter="/").replace("/","-"))       
            for col in df.columns[1:]:
                df[col] = df[col].apply(lambda x: clean_number_text(x))
                df[col] = pd.to_numeric(df[col], errors="coerce")
                df[col] = df[col].fillna(0.0)
            df.to_csv(self.broker_hold_filepath, index=False)
            return df
        else:
            return pd.read_csv(self.broker_hold_filepath)
    
    def get_main_trade(self, stock_id=2330, start_date="2022-4-15", end_date="2022-4-15"):
        """ 富邦證券主力進出明細 """

        # 檢查歷史紀錄有無存過
        self.main_trade_filepath = os.path.join(
            self.data_positions["chip_aspect"], 
            f"maintrade_{stock_id}_{start_date}_{end_date}.csv"
        )
        if not os.path.exists(self.main_trade_filepath):

            self.headers["Content-Type"] = "text/html;Charset=big5"
            # 迴圈每日的前15主力明細
            def daterange(start_date, end_date):
                import datetime as dt
                start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
                end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
                for n in range(int((end_date - start_date).days) + 1):
                    yield start_date + dt.timedelta(n)

            concat_tables = []
            for curr_date in tqdm(daterange(start_date, end_date)):
                curr_date = curr_date.strftime("%Y-%m-%d")
                url_curr_date = "-".join([str(int(number)) for number in curr_date.split("-")])
                url = f"https://fubon-ebrokerdj.fbs.com.tw/z/zc/zco/zco.djhtm?a={stock_id}&e={url_curr_date}&f={url_curr_date}"
                res = self.changeUserAgentNProxy(
                    maxtimes_changeIp=5,
                    maxtimes_retry=3,
                    url=url,
                    method="get",
                    payload=None
                )
                res.encoding = "big5"
                soup = BeautifulSoup(res.content, "html.parser")
                startpoint = len(soup.find_all("tr", {"id": "oScrollHead"})) + len(soup.find_all("tr", {"id": "oScrollMenu"}))
                if startpoint >= 6:
                    table = soup.find("table", {"class": "t01"}).find_all("tr")[startpoint+2:-3]
                    table = [[td.text for td in tr.find_all("td")] for tr in table]
                    table = [[curr_date] + row[:5] for row in table] + [[curr_date] + row[5:] for row in table]
                    concat_tables.extend(table)

            df = pd.DataFrame(
                concat_tables, 
                columns=["日期","券商","買進張數","賣出張數","買賣超張數","佔成交比重"]
            )
            cols = ["買進張數","賣出張數","買賣超張數","佔成交比重"]
            for col in cols:
                df[col] = df[col].fillna("0")
                if col != "佔成交比重":
                    df[col] = df[col].apply(lambda x: x.replace(",",""))
                    df[col] = df[col].astype(int)
                else:
                    df["佔成交比重"] = df["佔成交比重"].apply(lambda x: x.replace("%",""))
                    df["佔成交比重"] = df["佔成交比重"].astype(float)
            df["買賣超張數"] = df["買進張數"] - df["賣出張數"]
            df.to_csv(self.main_trade_filepath, index=False)
            return df
        else:
            return pd.read_csv(self.main_trade_filepath)

