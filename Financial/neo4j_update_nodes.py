from fuzzychinese import FuzzyChineseMatch
import json
import os
import pandas as pd
from py2neo import Node, NodeMatcher, Graph, Relationship, RelationshipMatcher
import py2neo

print(py2neo.__version__)
from tqdm import tqdm


home_dir = "/home/abao.yang@cathayholdings.com.tw"
home_relpath = os.path.realpath(home_dir)
rawdata_dir = "forResearch/data/gcs/Crawling/Financial/data"
all_securities_filepath = os.path.join(
    home_relpath, rawdata_dir, "company_basicinfo_all_securities.json"
)
account_args = {
    "hostname": "10.0.10.6",
    "username": "neo4j",
    "password": "neo4jj",
    "database": "test2",
}

# 取得所有股票名稱
with open(all_securities_filepath, "r", encoding="utf-8") as f:
    all_secur = json.load(f)
# print(all_secur["1101"])

comp_id_names = [
    (key, all_secur[key]["股票名稱"])
    for key in all_secur.keys()
    if all_secur[key].get("股票名稱")
]
df_comp = pd.DataFrame(comp_id_names, columns=["id", "name"])
# print(df_comp)
comp_names = [item[1] for item in comp_id_names]
# print(comp_names.index("欣欣"))

# 取得圖譜中現存股票名稱
cypher_q = """
    MATCH (n:公司) RETURN n.name
"""
graph = Graph(
    host=account_args["hostname"],
    auth=(account_args["username"], account_args["password"]),
    name=account_args["database"],
)
comp_names_in_graph = [i["n.name"] for i in graph.run(cypher_q).data()]

# 比對名稱
fuzzy_options = pd.Series(comp_names)
fcm = FuzzyChineseMatch(ngram_range=(3, 3), analyzer="stroke")
fcm.fit(fuzzy_options)
names_to_match = pd.Series(comp_names_in_graph)
top1_sim = fcm.transform(names_to_match, n=1)
fuzzy_match = pd.DataFrame(
    {
        "input": names_to_match,
        "top1_similar": top1_sim.reshape(-1),
        "similarity": fcm.get_similarity_score().reshape(-1),
    }
)
fuzzy_match = pd.merge(
    fuzzy_match, df_comp, left_on="top1_similar", right_on="name", how="left"
)
name_mapped = (
    fuzzy_match[fuzzy_match["similarity"] >= 0.8]
    .reset_index(drop=True)[["id", "input", "top1_similar"]]
    .values
)
mapping = {}
for item in name_mapped:
    mapping.update({item[1]: (item[0], item[2])})
# print(mapping)

# 存屬性到相對應節點
type = "公司"
nodematcher = NodeMatcher(graph)
for node_name in list(mapping.keys()):
    print(node_name)
    stock_id = mapping[node_name][0]
    print(stock_id)
    stock_name = mapping[node_name][1]
    node = nodematcher.match(type, name=node_name).first()
    for k in [
        "公司名稱",
        "英文簡稱",
        "統一編號",
        "產業別",
        "上市/上櫃",
        "股票代號",
        "股票名稱",
        "公司電話",
        "網址",
        "公司地址",
    ]:
        try:
            node.update({k: all_secur[stock_id][k]})
        except:
            if k == "公司電話":
                k = "總機電話"
                node.update({k: all_secur[stock_id][k]})

    graph.push(node)
