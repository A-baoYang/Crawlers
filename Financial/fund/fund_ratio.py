from utils import *

init_logger(filename="proxy_moneydj_fund_20220519.log")

output_dir = os.path.join(data_rootpath, "Financial/data/fund")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
output_filepath = os.path.join(output_dir, f"fund_ratio.json")
valid_ips = pd.read_csv(smartproxy_filepath).ip.values.tolist()
url = 'https://www.moneydj.com/funddj/yb/YP301000.djhtm'
user_token = "YWJhb3lhbmc6WUd5YW5nNjE1dGhlYmVzdA&&"
headers["authorization"] = f"Basic {user_token}",
headers["cookie"] = f"USER={user_token}",
maxtimes_changeIp = 5
maxtimes_retry = 3
res = changeUserAgentNProxy(
    maxtimes_changeIp=maxtimes_changeIp,
    maxtimes_retry=maxtimes_retry,
    url=url,
    method="get",
    payload=None,
    headers=headers,
    user_agent_list=user_agent_list,
    valid_ips=valid_ips,
).content

