# https://www.databricks.com/dataaisummit/sessions/
import os
import yaml


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
print(video_links)
if video_links:
    for v in video_links:
        cmd = f'python download_yt.py --video_url "{v}"'
        print(cmd)
        os.system(cmd)
