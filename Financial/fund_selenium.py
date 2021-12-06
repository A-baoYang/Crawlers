from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(ChromeDriverManager().install())
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import numpy as np
from tqdm import tqdm
import re
import pandas as pd


url = 'https://www.moneydj.com/funddj/yb/YP301000.djhtm'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'
chrome_path = 'C:/Users/Administrator/.wdm/drivers/chromedriver/win32/92.0.4515.107/chromedriver.exe'
opt = webdriver.ChromeOptions()
opt.add_argument('--user-agent=%s' % user_agent)


# catch type of funds
driver = webdriver.Chrome(executable_path=chrome_path, options=opt)
driver.set_window_size(1024, 850)
driver.get(url)
sleep(1)
fund_types = [(item.text, item.get_attribute('href')) for item 
              in driver.find_elements_by_xpath('//div[@class="InternalSearch"]//a')]
print(fund_types[:5])

fund_company_list = list()
for item in tqdm(fund_types):
    driver.get(item[1])
    fund_company = [(item.text, item.get_attribute('href')) for item 
                         in driver.find_elements_by_xpath('//table[@id="oMainTable"]//td/a') if len(item.text.strip()) > 0]
    print(fund_company[:6])
    fund_list = fund_company[0::2]
    print(fund_list[:3])
    company_list = fund_company[1::2]
    company_list = [item[0] for item in company_list]
    print(company_list[:3])
    for i in range(len(fund_list)):
        fund_company_list += [(company_list[i], fund_list[i][0], fund_list[i][1])]
    
    sleep(np.random.randint(3, 7))
    
    
driver.quit()



# catch ratio of funds
driver = webdriver.Chrome(executable_path=chrome_path, options=opt)
driver.set_window_size(1024, 850)
fund_url = 'https://www.moneydj.com/funddj/yl/yp013000.djhtm?a=ACFP72'
driver.get(fund_url)
sleep(15)


fund_ratio = dict()
fund_id_name_mapping = dict()

for fund in tqdm(fund_company_list):
    
    fund_name = fund[1]
    fund_id = fund[2].split('a=')[-1]
    fund_id_name_mapping.update({fund_id: fund_name})
    
    fund_url = f'https://www.moneydj.com/funddj/yl/yp013000.djhtm?a={fund_id}'
    driver.get(fund_url)
    try:
        ratio_content = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//table[@class="t04"]//table[@class="t01"]/tbody')))
        ratio_content = ratio_content.text
    except:
        print(fund_url)
        ratio_content = ' '
    
    finally:
        fund_ratio.update({fund_id: ratio_content})
        
    sleep(np.random.randint(3, 7))


driver.quit()


# store to json file
with open('fund_element_ratio_tables.json', 'w', encoding='utf-8') as f:
    json.dump(fund_ratio, f, ensure_ascii=False, indent=4)
    
with open('fund_id_name_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(fund_id_name_mapping, f, ensure_ascii=False, indent=4)

    
# 只存股票項目不存比例
fund_ratio_simple = dict()
for k in fund_ratio.keys():
    
    content = ' '.join(fund_ratio[k].split('\n')[3:])
    cl = np.unique([char.strip() for char in re.findall(r'[\u4e00-\u9fff- a-zA-Z]+|91APP', content) 
                    if (char.strip() != '') and (char.strip() != '-') 
                    and (char.strip() != 'KY') and (char.strip() != '-KY')]).tolist()
    
    fund_ratio_simple.update({k: cl})


# store to json file
with open('fund_holdings.json', 'w', encoding='utf-8') as f:
    json.dump(fund_ratio_simple, f, ensure_ascii=False, indent=4)

    
# 轉存 3 元組為 csv
collect = list()
for k in tqdm(fund_ratio_simple.keys()):
    for item in fund_ratio_simple[k]:
        collect += [(k, '持有', item)]

print(len(collect))
pd.DataFrame(collect, columns=['fund_id', 'rel', 'target_name']).drop_duplicates().to_csv('fund_holding_relation.csv', index=False)


