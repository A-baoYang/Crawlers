# https://www.databricks.com/dataaisummit/sessions/
import os
import yaml
from download_yt import download

def read_yaml(path: str):
    if path.endswith(".yaml"):
        with open(path, "r") as stream:
            try:
                return yaml.safe_load(stream)

            except yaml.YAMLError as e:
                print(e)
                return
    else:
        return


video_links = read_yaml("video_links.yaml")
for v in video_links[132:]:
    download(video_url=v)
