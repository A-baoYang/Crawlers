#%%
from collections import Counter
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
import plotly.express as px


#%%
data = pd.read_csv("latest_month.csv")
data
# %%
data["draw_results"] = data["draw_results"].apply(
    # lambda x: [int(n) for n in x.split(" ")]
    lambda x: [int(n) for n in eval(x)]
)
data["date"] = data["date"].astype(str)
data["special_number"] = data["special_number"].astype(int)
data
# %%
selected = data.copy()
print(selected.shape)
counter_0129 = dict(Counter(selected["draw_results"].sum()))

# %%
df_ = pd.DataFrame(
    {
        "number": counter_0129.keys(),
        "counts": counter_0129.values(),
    }
)
df_ = df_.sort_values("counts", ascending=False)
df_
# df_["perc"] = np.round(df_["counts"] / 203, 3)
# %%
# %%
df_[df_["number"] == 80]

# %%
df_.head(10)

# %%
def pick_sets(x, item_set):
    res = 1
    for item in item_set:
        if item not in x:
            res = 0
        else:
            pass
    return res


# %%
data["pick_res"] = data["draw_results"].apply(lambda x: pick_sets(x, [2, 44, 52]))
data
# %%
data[data["pick_res"] == 1].groupby(["date"]).agg({"draw_id": "count"})
# %%
# 從一個月內、各個數字的當日頻次來看 是否趨於隨機
data_ana = data[["date", "draw_time", "draw_id", "draw_results"]]
data_ana.reset_index()
# %%
data_ana = pd.merge(
    data_ana.reset_index(),
    data_ana["draw_results"]
    .explode()
    .reset_index()
    .rename(columns={"draw_results": "draw_number"}),
    on="index",
    how="left",
).drop("draw_results", axis=1)

data_ana

# %%
number_count_by_date = (
    data_ana.groupby(["draw_number", "date"])
    .agg({"draw_id": "count"})
    .reset_index()
    .rename(columns={"draw_id": "count"})
)

number_count_by_time = (
    data_ana.groupby(["draw_number", "draw_time"])
    .agg({"draw_id": "count"})
    .reset_index()
    .rename(columns={"draw_id": "count"})
)
# %%
px.line(number_count_by_date, x="date", y="count", color="draw_number")

# %%
data_ana
# %%
data_pivot = pd.pivot_table(
    data_ana,
    index="index",
    columns="draw_number",
    values="draw_id",
    aggfunc=lambda x: x.count(),
    fill_value=0,
)
data_pivot

# %%
data_pivot.head(1)
# %%
# 共現矩陣
data_pivot_self_dot = data_pivot.T.dot(data_pivot)
# %%
np.fill_diagonal(data_pivot_self_dot.values, 0)
data_pivot_self_dot

# %%
data_pivot_self_dot.to_csv("latest_month_co_occurrence.csv")
# %%
data_pivot_self_dot[[1]].sort_values(1, ascending=False)
data_pivot_self_dot[[68]].sort_values(68, ascending=False)

# %%
data_pivot_self_dot

# %%
from mlxtend.frequent_patterns import apriori
from mlxtend.preprocessing import TransactionEncoder

# %%
encoder = TransactionEncoder().fit(data["draw_results"].tolist())
onehot = encoder.transform(data["draw_results"].tolist())
onehot = pd.DataFrame(onehot, columns=encoder.columns_)
onehot.head()
# %%
# Compute the support
support = onehot.mean()
support = pd.DataFrame(support, columns=["support"]).sort_values(
    "support", ascending=False
)
# %%
support.head()
support.describe()

# %%
# Compute support for burgers and french fries
supportBF = np.logical_and(onehot[1], onehot[2]).mean()

# Compute support for burgers and mineral water
supportBM = np.logical_and(onehot[2], onehot[3]).mean()

# Compute support for french fries and mineral water
supportFM = np.logical_and(onehot[1], onehot[3]).mean()

# Print support values
print("burgers and french fries: %.2f" % supportBF)
print("burgers and mineral water: %.2f" % supportBM)
print("french fries and mineral water: %.2f" % supportFM)

# %%
frequent_itemsets = apriori(
    onehot, min_support=0.01, max_len=5, use_colnames=True
).sort_values("support", ascending=False)
frequent_itemsets.shape
frequent_itemsets.head(30)

# %%
# frequent_itemsets = frequent_itemsets
# frequent_itemsets.head(100).reset_index
# %%
