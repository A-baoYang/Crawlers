# %%
import json
from py2neo import Node, NodeMatcher, Graph, Relationship, RelationshipMatcher
import py2neo

print(py2neo.__version__)
from tqdm import tqdm


# %%
class DataToNeo4j(object):
    def __init__(self, host, username, password, database):
        """
        連接 Neo4j 資料庫
        """
        link = Graph(host=host, auth=(username, password), name=database)
        self.graph = link
        self.nodematcher = NodeMatcher(self.graph)
        self.relationmatcher = RelationshipMatcher(self.graph)
        # self.ent = 'ent'
        # self.graph.delete_all()

    def create_node(self, node_list):
        """
        創建節點；若相同節點已存在則不創建，避免重複節點產生
        """
        for node in tqdm(node_list):
            name = node["name"]
            type = node["type"]

            if not self.nodematcher.match(type, name=name).first():
                name_node = Node(type, name=name)
                for k in node.keys():
                    if k not in ["name", "type"]:
                        name_node[k] = node[k]

                self.graph.create(name_node)

    def create_relation(self, data):
        """
        比對存在節點類型及名稱，創建節點間的關係
        """
        for rel_set in tqdm(data):
            ent1 = rel_set[0]
            ent1_node = self.nodematcher.match(ent1["type"], name=ent1["name"]).first()
            ent2 = rel_set[2]
            ent2_node = self.nodematcher.match(ent2["type"], name=ent2["name"]).first()
            rel = rel_set[1]
            rel_in_graph = self.relationmatcher.match(
                nodes=(ent1_node, ent2_node), r_type=rel["name"]
            ).first()
            try:
                # 投資、訂單關係修正，去冗餘
                if ("投資" in rel["name"]) or ("訂單" in rel["name"]):
                    if len(rel["name"]) >= 2:
                        rel["name"] = rel["name"][-2:]
                    if rel["name"] in ["投資", "下訂單"]:
                        ent1 = rel_set[0]
                        ent2 = rel_set[2]
                    if rel["name"] in ["被投資", "接訂單"]:
                        ent1 = rel_set[2]
                        ent2 = rel_set[0]

                if rel_in_graph:
                    if type(rel_in_graph["date"]) == str:
                        rel_in_graph["date"] = [rel_in_graph["date"]]
                    if rel["date"] not in rel_in_graph["date"]:
                        rel_in_graph["date"].append(rel["date"])
                else:
                    new_rel_in_graph = Relationship(ent1_node, rel["name"], ent2_node)
                    for k in rel.keys():
                        if k == "date":
                            new_rel_in_graph[k] = [rel[k]]
                        elif k not in ["name", "date"]:
                            new_rel_in_graph[k] = rel[k]
                    self.graph.create(new_rel_in_graph)

            except AttributeError as e:
                print(e)
                print(f"Happen at {rel_set}")


# %%
account_args = {
    "neo4j_hostname": "10.0.10.6",
    "neo4j_username": "neo4j",
    "neo4j_password": "neo4jj",
    "neo4j_database": "dstinternal",
}

create_data = DataToNeo4j(
    host=account_args["neo4j_hostname"],
    username=account_args["neo4j_username"],
    password=account_args["neo4j_password"],
    database=account_args["neo4j_database"],
)

# %%
static_rel_file = (
    "../../forResearch/data/gcs/Crawling/Financial/data/static_node_rels.json"
)
dynamic_rel_file = "../../forDevTest/test_finKG/model_data/output/FinKG-company_relations-20220207.json"

with open(static_rel_file, "r", encoding="utf-8") as f:
    static_node_rels = json.load(f)

with open(dynamic_rel_file, "r", encoding="utf-8") as f:
    dynamic_news_rels = json.load(f)

# %%
# static_node_rels = static_node_rels[:100]
# dynamic_news_rels = dynamic_news_rels[:1000]
node_list = [item[0] for item in static_node_rels] + [
    item[2] for item in static_node_rels
]

dynamic_news_rels = [item["extract_relations"] for item in dynamic_news_rels]
print(f"Length of company relations: {len(dynamic_news_rels)}")
print(dynamic_news_rels[0])

dynamic_node_list, dynamic_name_list = list(), list()
for node in dynamic_news_rels:
    for node_id in [0, 2]:
        if node[node_id]["name"] not in dynamic_name_list:
            dynamic_node_list.append(node[node_id])
            dynamic_name_list.append(node[node_id]["name"])

# %%
# static
create_data.create_node(node_list=node_list)
# %%
create_data.create_relation(data=static_node_rels)

# %%
# dynamic
create_data.create_node(node_list=dynamic_node_list)
# %%
create_data.create_relation(data=dynamic_news_rels)

# %%
