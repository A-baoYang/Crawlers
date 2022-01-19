# %%
import json
from py2neo import Node, NodeMatcher, Graph, Relationship
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
        self.matcher = NodeMatcher(self.graph)
        # self.ent = 'ent'
        # self.graph.delete_all()

    def create_node(self, node_list):
        """
        創建節點；若相同節點已存在則不創建，避免重複節點產生
        """
        for node in tqdm(node_list):
            name = node["name"]
            type = node["type"]
            labels = dict()
            for k in node.keys():
                if k not in labels.keys():
                    labels.update({k: node[k]})

            if not self.matcher.match(type, name=name).first():
                name_node = Node(type, name=name)
                for k in node.keys():
                    if k not in ["name","type"]:
                        

                if labels:
                    for k in labels.keys():
                        name_node[k] = labels[k]

                self.graph.create(name_node)

    def create_relation(self, data):
        """
        比對存在節點類型及名稱，創建節點間的關係
        """
        for rel_set in tqdm(data):
            ent1 = rel_set[0]
            ent2 = rel_set[2]
            rel = rel_set[1]
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

                relationship = Relationship(
                    self.matcher.match(ent1["type"], name=ent1["name"]).first(),
                    rel["name"],
                    self.matcher.match(ent2["type"], name=ent2["name"]).first(),
                )
                for k in rel.keys():
                    if k != "name":
                        relationship[k] = rel[k]

                self.graph.create(relationship)

            except AttributeError as e:
                print(e)
                print(f"Happen at {rel_set}")


# %%
account_args = {
    "neo4j_hostname": "10.0.10.6",
    "neo4j_username": "neo4j",
    "neo4j_password": "neo4jj",
    "neo4j_database": "test",
}

create_data = DataToNeo4j(
    host=account_args["neo4j_hostname"],
    username=account_args["neo4j_username"],
    password=account_args["neo4j_password"],
    database=account_args["neo4j_database"],
)

# %%
with open("data/static_node_rels.json", "r", encoding="utf-8") as f:
    static_node_rels = json.load(f)

# %%
node_list = [item[0] for item in static_node_rels] + [
    item[2] for item in static_node_rels
]

# %%
create_data.create_node(node_list=node_list)

# %%
create_data.create_relation(data=static_node_rels)

# %%
static_node_rels

# %%
