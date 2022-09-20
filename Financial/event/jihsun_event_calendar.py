from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

# driver = webdriver.Chrome(ChromeDriverManager().install())
from time import sleep
import pandas as pd
from utils import *


if __name__ == "__main__":

    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"
    chrome_path = (
        "/Users/jiunyiyang/.wdm/drivers/chromedriver/mac64/105.0.5195.52/chromedriver"
    )
    opt = webdriver.ChromeOptions()
    opt.add_argument("--user-agent=%s" % user_agent)
    start_date = 20220918
    event_df = pd.DataFrame()
    driver = webdriver.Chrome(executable_path=chrome_path, options=opt)

    while start_date > 20100101:
        date_list, y, m, d = gen_date_list(start_date, days=14)
        start_date, date_list = date_list[-1], date_list[:-1]

        try:
            sleep(1)
            url = f"https://jsjustweb.jihsun.com.tw/z/ze/zej/zej.djhtm?A=0&B={y}-{m}-{d}&C=-2"
            driver.get(url)
            content = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, "//table"))
            )[-1]
            data = [item.strip() for item in content.text.split(" ") if item.strip()]
            data = [item.split("\n") for item in data]
            # split item which mixed date & event
            data = clean_mixed_item(data)
            # record date item position
            date_ids = gen_date_positions(data)
            assert len(date_ids) == len(date_list)
            # arrange events
            events = arrange_events(data, date_ids, date_list)
            start_date = int("".join(date_list[0].split("/")))
            # store as csv
            for k, v in events.items():
                df = pd.DataFrame(v, columns=["stock_id", "stock_name", "event_name"])
                df["date"] = k
                event_df = pd.concat([event_df, df])
            event_df.to_csv("stock-regular-events.csv", index=False)
            print(start_date, "stored")

        except Exception as e:
            print(e)
            driver.close()

    driver.close()
