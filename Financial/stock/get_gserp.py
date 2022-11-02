#%%
# https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
from ckiptagger import WS, POS, NER
from collections import Counter
import inspect
import json
import os
import pandas as pd
import re
import sys
import warnings
warnings.filterwarnings("ignore")

# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0, parentdir)

from utils import *

#%%
def load_proxy(filepath):
    return pd.read_csv(filepath)


def load_ent_list(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def store_dict(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_serp_titles(search_text):
    url = "https://www.google.com/search"
    url_params = {
        "as_q": search_text,
        "as_epq": "",
        "as_oq": "",
        "as_eq": "",
        "as_nlo": "",
        "as_nhi": "",
        "lr": "",
        "cr": "",
        "as_qdr": "all",
        "as_sitesearch": "tw.stock.yahoo.com",
        "as_occt": "any",
        "safe": "images",
        "as_filetype": "",
        "tbs": ""
    }
    proxy_list = load_proxy(smartproxy_filepath).ip.values.tolist()
    r = changeUserAgentNProxy(
        maxtimes_changeIp=5,
        maxtimes_retry=3,
        url=url,
        params=url_params,
        method="get",
        payload=None,
        headers=headers,
        valid_ips=proxy_list
    ).content
    soup = BeautifulSoup(r, "html.parser")
    for res_list in [
        [item.text for item in soup.find_all("h3")],
        [item.text for item in soup.find_all("span", {"class": "CVA68e qXLe6d fuLhoc ZWRArf"})]
    ]:
        if res_list:
            return res_list
    return []

def filter_stock_id(input_text):
    _id_regex = "\d+\.[a-zA-Z]+"
    stock_id = re.search(_id_regex, input_text)
    if stock_id:
        stock_name = re.split(_id_regex, input_text)[0][:-1]
        return f"{stock_id.group()}-{stock_name}"
    else:
        return 0


def do_ner(input_text, res_collect):
    ws_list = ckiptagger_ws(input_text)
    pos_list = ckiptagger_pos(ws_list)
    ner_list = list(ckiptagger_ner(ws_list, pos_list)[0])
    del pos_list, ws_list
    for item in ner_list:
        type = item[2]
        name = item[3]
        if type not in res_collect:
            res_collect.update({type: [name]})
        else:
            res_collect[type].append(name)
    return res_collect


if __name__ == "__main__":
    
    init_logger(filename="../../logs/get_gserp.log")

    # NER model
    ckiptagger_model_path = "/home/abao.yang@cathayholdings.com.tw/forResearch/data/gcs/ckiptagger_data"
    ckiptagger_ws = WS(ckiptagger_model_path)
    ckiptagger_pos = POS(ckiptagger_model_path)
    ckiptagger_ner = NER(ckiptagger_model_path)

    # load ent list from KGBuilder entity_extraction.json
    data = load_ent_list(
        filepath="/home/abao.yang@cathayholdings.com.tw/forDevTest/test_finKG/model_data/output/entity_extraction-output-20220513_20220519.json")
    # ent_list = ["台達","台積","大聯大","南亞","力晶"]
    ent_list = []
    for piece in tqdm(data):
        ent_list += piece["entity_extract"]["ORG"]
    ent_list = list(set(ent_list))
    pd.DataFrame({"ent": ent_list}).to_csv("ent_list", index=False)

    ner_from_gserp = {}
    for ent in tqdm(ent_list):
        try:
            # 爬蟲
            titles = get_serp_titles(search_text=ent)
            logger.info(titles)
            _res = {"stock": []}
            for title in titles:
                # 股票代號
                stock = filter_stock_id(input_text=title)
                if stock:
                    _res["stock"].append(stock)
                # NER 輸出&統整
                _res = do_ner(input_text=[title], res_collect=_res)

            new_res = {}
            for k in ["stock", "ORG"]:
                if k in _res:
                    new_res[k] = {k: v for k, v in dict(Counter(_res[k])).items() if v}
            ner_from_gserp.update({ent: new_res})
        except Exception as e:
            logger.info(f"Error at {ent} - {e}")
            ner_from_gserp.update({ent: {}})
        finally:
            store_dict(
                filepath="ner_from_gserp.json", 
                data=ner_from_gserp)

