from bs4 import BeautifulSoup
import datetime as dt
import json
import numpy as np
import pandas as pd
import requests
import time
from tqdm import tqdm


headers = {
    "authority": "lotto.auzonet.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "cookie": "PHPSESSID=dvhdfejfbepnck4vm70o13v0r3",
    "if-modified-since": "Sat, 29 Jan 2022 15:52:09 GMT",
    "if-none-match": 'W/"61f562a9-1299"',
    "origin": "https://lotto.auzonet.com",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "referer": "https://lotto.auzonet.com/bingobingo.php",
    "dnt": "1",
    "upgrade-Insecure-Requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
}


def fetch_latest_draw():
    url = "https://sg.cdn.lotto.auzonet.com/cache/app/history_bingobingo.json"
    res = requests.get(url, headers=headers).content
    res = json.loads(res)
    return res


# test requests
if __name__ == "__main__":
    history_bingo_rows = list()
    day_num = 30
    date_list = [dt.datetime.today() - dt.timedelta(days=x) for x in range(day_num)]
    for date in tqdm(date_list):

        time.sleep(1)

        date = dt.datetime.strftime(date, "%Y%m%d")
        date_url = f"https://lotto.auzonet.com/bingobingo/list_{date}.html"

        res = requests.get(date_url, headers=headers).content
        soup = BeautifulSoup(res, "html.parser")
        bingo_row = [
            (
                date,
                item.find("td", {"class": "BPeriod"}).text,
                [
                    number.text
                    for number in item.find("td", {"align": "center"}).find_all("div")
                ],
                [
                    number.text
                    for number in item.find("td", {"align": "center"}).select(
                        'div[class*="s"]'
                    )
                ],
                [val.text for val in item.find_all("td", {"class": "Bf21b"})],
            )
            for item in soup.find_all("tr", {"class": "bingo_row"})
        ]

        history_bingo_rows += bingo_row

    df = pd.DataFrame(
        history_bingo_rows,
        columns=["date", "draw_id", "draw_results", "special_number", "other"],
    )
    df["draw_time"] = df["draw_id"].apply(lambda x: str(x)[-5:])
    df["draw_id"] = df["draw_id"].apply(lambda x: str(x)[:-5])
    df["special_number"] = df["special_number"].apply(
        lambda x: x[0] if len(x) == 1 else "err"
    )
    df = pd.concat(
        [
            df,
            pd.DataFrame(
                df["other"].tolist(),
                columns=["number_remains", "guess_size", "guess_odd"],
            ),
        ],
        axis=1,
    ).drop(["other"], axis=1)

    df.to_csv("latest_month.csv", index=False)
