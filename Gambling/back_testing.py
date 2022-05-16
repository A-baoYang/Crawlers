#%%
import datetime as dt
import pandas as pd

from crawler import fetch_latest_draw

#%%
today = dt.datetime.today().date().strftime("%Y%m%d")
res = fetch_latest_draw()
data = (
    pd.DataFrame(res)
    .drop(["LottoName", "DrawContinuously", "DrawballClass"], axis=1)
    .sort_values("Period", ascending=False)
)
data["date"] = today

# %%
data["Drawball"][0]
# %%
# https://www.taiwanlottery.com.tw/BINGOBINGO/index.asp#02
# 獎金計算公式化
