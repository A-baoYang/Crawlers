from glob import glob
import json
import os
from tqdm import tqdm


filepath = "3high_gsrp_articles_2.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

keys = ["高血壓飲食禁忌", "高血壓形成原因"]

for key in keys:
    print(type(data[key][0][-1].encode("utf-8")))

# paths = sorted(glob("3high_gsrp_keywords_lv*"))

# for pid in tqdm(range(len(paths) - 1, 0, -1)):

#     with open(paths[pid - 1], "r", encoding="utf-8") as f:
#         data_node = json.load(f)
#     search_related_tree = data_node.copy()

#     if pid == 7:
#         with open(paths[pid], "r", encoding="utf-8") as f:
#             data_leaf = json.load(f)

#     for node_k in data_node.keys():
#         search_related_tree[node_k] = {}
#         for node_v in data_node.get(node_k):
#             for leaf_k in data_leaf.keys():
#                 if node_v == leaf_k:
#                     search_related_tree[node_k].update({node_v: data_leaf[leaf_k]})

#     data_leaf = search_related_tree.copy()

# =====

# def get_recursive_keys(dictionary):
#     all_keys = []
#     for key, value in dictionary.items():
#         all_keys.append(key)
#         if type(value) is dict:
#             all_keys += get_recursive_keys(value)
#     return all_keys


# with open("3high_gsrp_keywords_tree.json", "w", encoding="utf-8") as f:
#     json.dump(search_related_tree, f, ensure_ascii=False, indent=4)
