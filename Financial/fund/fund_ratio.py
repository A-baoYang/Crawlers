#%%
from utils import *

#%%
month = 6
init_logger(filename=f"proxy_moneydj_fund-2022{str(month).zfill(2)}.log")

output_dir = os.path.join(data_rootpath, "Financial/data", "fund")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)
output_filepath = os.path.join(output_dir, f"fund_ratio-{str(month).zfill(2)}.json")
# valid_ips = pd.read_csv(smartproxy_filepath).ip.values.tolist()
url = 'https://www.moneydj.com/funddj/yp/yp013000.djhtm?a=AC0051'
user_token = "YWJhb3lhbmc6WUd5YW5nNjE1dGhlYmVzdA&&"
headers["authorization"] = "Basic YWJhb3lhbmc6WUd5YW5nNjE1dGhlYmVzdA&&"
headers["cookie"] = "USER=YWJhb3lhbmc6WUd5YW5nNjE1dGhlYmVzdA&&"
headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
headers["Content-Type"] = "text/html;Charset=big5"

#%%
res = requests.get(url, headers=headers)
res.content
#%%
res.encoding = "big5-hk"
soup = BeautifulSoup(res.content, "html.parser")
soup

# maxtimes_changeIp = 5
# maxtimes_retry = 3
# res = changeUserAgentNProxy(
#     maxtimes_changeIp=maxtimes_changeIp,
#     maxtimes_retry=maxtimes_retry,
#     url=url,
#     method="get",
#     payload=None,
#     headers=headers,
#     user_agent_list=user_agent_list,
#     valid_ips=valid_ips,
# ).content


# %%
