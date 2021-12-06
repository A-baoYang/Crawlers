from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())

from time import sleep
import re
import pandas as pd

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'
chrome_path = 'C:/Users/Administrator/.wdm/drivers/chromedriver/win32/92.0.4515.107/chromedriver.exe'
url = 'https://www.tej.com.tw/webtej/doc/uid.htm'


opt = webdriver.ChromeOptions()
opt.add_argument('--user-agent=%s' % user_agent)
driver = webdriver.Chrome(executable_path=chrome_path, options=opt)
driver.set_window_size(1024, 850)
driver.get(url)
text = [item.text for item in driver.find_elements_by_xpath('//font')]
sleep(1)
driver.quit()

end = text.index('上櫃公司代碼一覽表')
start = text.index('1101   台泥')
stock_comp = [item.strip() for item in text[start:end] if (item.strip() != '') and re.findall('[0-9]+', item)]
stock_names = [item.split(' ')[-1].strip() for item in stock_comp]
stock_ids = [item.split(' ')[0].strip() for item in stock_comp]

df_stock_comp = pd.DataFrame([stock_ids, stock_names]).T
df_stock_comp.columns = ['id', 'name']
print(df_stock_comp.head())
df_stock_comp.to_csv('df_stock_comp.csv', index=False)
