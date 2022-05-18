# Crawlers
Python scripts for crawling several different websites.

## Taiwan Stock

### 法人基本資訊
> 公司
- [上市公司股票列表](https://www.tej.com.tw/webtej/doc/uid.htm)
  - `stockname_selenium.py`
- [證券代號總表](https://isin.twse.com.tw/isin/C_public.jsp?strMode=2)
  - `get_securities_id.py`
- 公司基本資料
  - [Goodinfo](https://goodinfo.tw/tw/BasicInfo.asp?STOCK_ID=2330)
  - [MoneyDJ](https://concords.moneydj.com/z/zc/zca/zca.djhtm?a=2330)
  - `company_crawler.py`
> 投信機構
- [國內基金投信公司列表](https://www.yesfund.com.tw/w/wp/wp00.djhtm)
- [台灣外資券商列表](https://www.cmoney.tw/notes/note-detail.aspx?nid=50427)
> 基金
- [國內基金列表](https://www.moneydj.com/funddj/yb/YP301000.djhtm)
  - `fund_selenium.py`
- [國內外 ETF 列表](https://www.moneydj.com/ETF/X/Basic/Basic0007.xdjhtm?etfid=2824.HK)
  - `base_crawler.ipynb`


### 法人關聯資訊
> 公司-公司
- 產業鏈關係(上下游) (tpex)
  - [產業鏈及公司對照表](https://ic.tpex.org.tw/introduce.php?ic=D000)
    - `base_crawler.ipynb`
- 子公司關係
  - [Wikidata > subsidiary](https://www.wikidata.org/wiki/Q463094)
  - [公開資訊觀測站 > 重要子公司基本資料彙總表](https://mops.twse.com.tw/mops/web/t79sb04)
- 投資關係
  - [Crunchbase > Investments](https://www.crunchbase.com/organization/tsmc/company_financials)
- 供應鏈/客戶關係
  - [MoneyDJ > 公司互動](https://concords.moneydj.com/Z/ZC/ZC0/ZC00/ZC00_2303.djhtm)
- *聯盟/競爭關係*
  - [MoneyDJ > 公司互動](https://concords.moneydj.com/Z/ZC/ZC0/ZC00/ZC00_2303.djhtm)
> 公司-產品
- [MoneyDJ > 基本資訊 > 主要產品/業務欄位](https://concords.moneydj.com/z/zc/zca/zca.djhtm?a=2330)
> 公司-產業
- [公司所屬類股、概念股、集團股列表](https://goodinfo.tw/StockInfo/StockList.asp?MARKET_CAT=上市)
  - `company_crawler.py`
> 人物-公司
- [董監事每月持股比例明細](https://mops.twse.com.tw/mops/web/ajax_stapap1)
  - `company_crawler.py`
- [Goodinfo > 高層欄位](https://goodinfo.tw/tw/BasicInfo.asp?STOCK_ID=2330)
> 基金-公司
- [國內基金持股比例](https://www.moneydj.com/funddj/yb/YP301000.djhtm)
  - `fund_selenium.py`
- 隸屬於 (moneydj) 
  - `基金 -[隸屬於]-> 投信機構`
> 投信機構-公司
- [每日前15主力進出明細](https://fubon-ebrokerdj.fbs.com.tw/z/zc/zco/zco.djhtm?a=2330&e=2022-4-14&f=2022-4-14)
  - `/stock_prediction/utils.py`


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
- [董監事每月持股比例明細](https://mops.twse.com.tw/mops/web/ajax_stapap1)
  - `company_crawler.py`
- [三大法人每日持股明細](https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcl/zcl.djhtm?a={stock_id}&c={start_date}&d={end_date})
- [前15主力進出明細](https://fubon-ebrokerdj.fbs.com.tw/z/zc/zco/zco.djhtm?a={stock_id}&e={url_curr_date}&f={url_curr_date})
  - `/stock_prediction/utils.py`


### 台灣財經媒體
- [自由時報 LTN > 「財經」新聞搜尋結果](https://search.ltn.com.tw/list?keyword=%E8%B2%A1%E7%B6%93&type=all&sort=date)
- [鉅亨網 CNYES > 台股新聞](https://news.cnyes.com/news/cat/tw_stock)
- [MONEYDJ > 即時新聞](https://www.moneydj.com/kmdj/news/newsreallist.aspx?index1=10&a=mb00)
- [經濟日報 MONEYUDN > 即時新聞](https://money.udn.com/rank/newest/1001/0/1)
- [Yahoo Finance 最新新聞](https://tw.news.yahoo.com/finance/)
  - 每次抓取單頁只有10-20篇，無法滾動取得更多，相對其他網域需提高頻率
- [CMoney 投資網誌](https://www.cmoney.tw/notes/?bid=22814)
- [科技新報 TECHNEWS](https://technews.tw/)
- [Goodinfo! > 個股相關新聞](https://goodinfo.tw/tw/StockAnnounceList.asp?PAGE=1&START_DT=2021%2F09%2F12&END_DT=2021%2F12%2F12&STOCK_ID={stock_id}&KEY_WORD=&NEWS_SRC=%E5%85%AC%E5%91%8A%E8%A8%8A%E6%81%AF&NEWS_SRC=Anue%E9%89%85%E4%BA%A8&NEWS_SRC=ETtoday%E6%96%B0%E8%81%9E%E9%9B%B2&NEWS_SRC=PR+Newswire)
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

