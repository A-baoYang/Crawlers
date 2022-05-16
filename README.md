# Crawlers
Python scripts for crawling several different websites.

## Taiwan Stock

### 法人基本資訊
> 公司
- 上市公司股票列表 (tej)
  - https://www.tej.com.tw/webtej/doc/uid.htm
  - `stockname_selenium.py`
- 證券代號總表 (twse)
  - https://isin.twse.com.tw/isin/C_public.jsp?strMode={page_id}
  - `get_securities_id.py`
- 公司基本資料
  - Goodinfo: https://goodinfo.tw/tw/BasicInfo.asp?STOCK_ID={stock_id}
  - MoneyDJ: https://concords.moneydj.com/z/zc/zca/zca.djhtm?a={stock_id}
  - `company_crawler.py`
> 基金
- 國內外基金列表
  - https://www.moneydj.com/funddj/yb/YP301000.djhtm
  - `fund_selenium.py`
- 國內外 ETF 列表
  - https://www.moneydj.com/ETF/X/Basic/Basic0007.xdjhtm?etfid=2824.HK
  - `base_crawler.ipynb`

### 法人關聯資訊
> 公司-公司
- 產業鏈位置關係(上下游) (tpex)
  - 各產業價值鏈及公司對照表
    - https://ic.tpex.org.tw/introduce.php?ic=D000
    - `base_crawler.ipynb`
- 供應鏈關係 (concords.moneydj)
- 子公司關係 (wikidata)
- 投資關係 (crunchbase)
- 客戶關係 (concords.moneydj)
- *聯盟關係(合作)* (concords.moneydj)
- *競爭關係* (concords.moneydj)
> 公司-產品
- 主要產品/業務列表 (goodinfo/concords.moneydj)
> 公司-產業
- 類股分類列表 (goodinfo)
  - 公司所屬類股、概念股、集團股列表
    - https://goodinfo.tw/StockInfo/StockList.asp?MARKET_CAT={type}
    - `company_crawler.py`
> 人物-公司
- 持股 (mose)
  - 董監事每月持股比例明細
    - https://mops.twse.com.tw/mops/web/ajax_stapap1
    - `company_crawler.py`
- 任職 (goodinfo)
> 基金-公司
- 持股 (moneydj)
  - 三大法人每日持股明細
    - https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcl/zcl.djhtm?a={stock_id}&c={start_date}&d={end_date}
  - 前15主力進出明細
    - https://fubon-ebrokerdj.fbs.com.tw/z/zc/zco/zco.djhtm?a={stock_id}&e={url_curr_date}&f={url_curr_date}
    - `/stock_prediction/utils.py`

- 隸屬於 (moneydj)
> 投信機構-公司
- 持股 (fubon/concords.moneydj)
- 隸屬於

### 台股財務面
- 公司每季財報基本面指標
  - TWSE


### 台股交易面/技術面
- 上市櫃公司股價
  - ranaroussi/yfinance
  - `/stock_prediction/utils.py`
- 技術指標
  - talib
  - bukosabino/ta
  - twopirllc/pandas-ta
- 產業指數
  - https://www.tpex.org.tw/web/stock/aftertrading/index_monthly/idxsm_result.php?l=zh-tw&d={d_0}/{d_1}
  - `/stock_prediction/utils.py`


### 台股籌碼面
- 董監事每月持股比例明細
  - https://mops.twse.com.tw/mops/web/ajax_stapap1
  - `company_crawler.py`
- 三大法人每日持股明細
  - https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcl/zcl.djhtm?a={stock_id}&c={start_date}&d={end_date}
- 前15主力進出明細
  - https://fubon-ebrokerdj.fbs.com.tw/z/zc/zco/zco.djhtm?a={stock_id}&e={url_curr_date}&f={url_curr_date}
  - `/stock_prediction/utils.py`


### 台灣財經媒體
- 自由時報 LTN
- 鉅亨網 CNYES
- MONEYDJ
- 經濟日報 MONEYUDN
- Yahoo 財經最新新聞
- CMoney 投資筆記
- 科技新報 TECHNEWS
- Goodinfo!
  - 個股相關新聞
    - https://goodinfo.tw/tw/StockAnnounceList.asp?PAGE=1&START_DT=2021%2F09%2F12&END_DT=2021%2F12%2F12&STOCK_ID={stock_id}&KEY_WORD=&NEWS_SRC=%E5%85%AC%E5%91%8A%E8%A8%8A%E6%81%AF&NEWS_SRC=Anue%E9%89%85%E4%BA%A8&NEWS_SRC=ETtoday%E6%96%B0%E8%81%9E%E9%9B%B2&NEWS_SRC=PR+Newswire
    - `company_crawler.py`


## 加密貨幣
### 交易所市場數據
- ccxi
- 技術指標：同台股

### 幣種消息
- FTX
- Twitter


------ (待整理) ------

## E-commerce

- Momo
- PChome
- Shopee
- Amazon

## Social Media

- PTT
- Mobile01
- Dcard
- Youtube

## Life
### GoogleMaps Reviews

