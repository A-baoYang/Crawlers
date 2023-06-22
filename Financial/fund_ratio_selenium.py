#%%
import json
import numpy as np
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

# driver = webdriver.Chrome(ChromeDriverManager().install())

#%%
url = "https://www.moneydj.com/funddj/yb/YP301000.djhtm"
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"
chrome_path = (
    "/Users/jiunyiyang/.wdm/drivers/chromedriver/mac64/102.0.5005.61/chromedriver"
)
opt = webdriver.ChromeOptions()
opt.add_argument("--user-agent=%s" % user_agent)

# load fund item list
with open("fund_company_dict.json", "r", encoding="utf-8") as f:
    fund_company_dict = json.load(f)
fund_company_list = fund_company_dict["list"]

#%%
# catch ratio of funds
account = "abaoyang"
password = "YGyang615thebest"

# catch ratio of funds
driver = webdriver.Chrome(executable_path=chrome_path, options=opt)
driver.set_window_size(1024, 850)
fund_url = "https://www.moneydj.com/funddj/yl/yp013000.djhtm?a=ACFP72"
driver.get(fund_url)
sleep(15)


fund_ratio = dict()

for fund in tqdm(fund_company_list):

    fund_name = fund[1]
    fund_id = fund[2].split("a=")[-1]
    fund_ratio.update({fund_id: dict()})
    fund_ratio[fund_id].update({"基金名稱": fund_name})

    info_url = "https://www.moneydj.com/funddj/yp/yp011000.djhtm?a=%s" % (fund_id)
    fund_url = "https://www.moneydj.com/funddj/yl/yp013000.djhtm?a=%s" % (fund_id)

    # 持股成分
    driver.get(fund_url)
    try:
        ratio_content = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//table[@class="t04"]//table[@class="t01"]//td[contains(@class, "t3")]',
                )
            )
        )
        ratio_content = [
            item.text
            for item in driver.find_elements_by_xpath(
                '//table[@class="t04"]//table[@class="t01"]//td[contains(@class, "t3")]'
            )
        ]
        ratio_content = (
            np.array(ratio_content).reshape(len(ratio_content) // 4, 4).tolist()
        )

        update_date = driver.find_element_by_xpath(
            '//table[@class="t04"]//td[@class="t3n1c1"]'
        ).text

    except:
        ratio_content = " "
        update_date = " "
        print(fund_url)

    finally:
        fund_ratio[fund_id].update({"更新時間": update_date})
        fund_ratio[fund_id].update({"持股": ratio_content})

    # 基本資料
    driver.get(info_url)
    try:
        info_col = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table[@class="t04"]//td[@class="t2c1"]')
            )
        )
        info_col = [
            item.text
            for item in driver.find_elements_by_xpath(
                '//table[@class="t04"]//td[@class="t2" or @class="t2c1"]'
            )
        ]
        info_val = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table[@class="t04"]//td[@class="t3t2"]')
            )
        )
        info_val = [
            item.text
            for item in driver.find_elements_by_xpath(
                '//table[@class="t04"]//td[@class="t3t2"]'
            )
        ]

    except Exception as e:
        print(e)
        info_col, info_val = list(), list()

    finally:
        res = dict(zip(info_col, info_val))
        fund_ratio[fund_id].update({"基本資料": res})

    # store to json file
    with open("fund_holdings_final.json", "w", encoding="utf-8") as f:
        json.dump(fund_ratio, f, ensure_ascii=False, indent=4)

    sleep(np.random.randint(3, 7))

driver.quit()


# store to json file
with open("fund_holdings_final.json", "w", encoding="utf-8") as f:
    json.dump(fund_ratio, f, ensure_ascii=False, indent=4)
