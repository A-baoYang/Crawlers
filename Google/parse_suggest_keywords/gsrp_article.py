import re
with open(all_keyword_filepath, "r", encoding="utf-8") as f:
    all_keyword = json.load(f)

for kw in tqdm(all_keyword["keywords"]):
    soup = fetch_gsrp(kw=kw)
    try:
        gsrp_articles = [
            (item.find("h3").text, item.find("a", href=True)["href"])
            for item in soup.find("div", id="rso").find_all(
                "div", {"class": ["g", "g tF2Cxc", "hlcw0c", "ULSxyf"]}
            )
        ]

        for item_id in tqdm(range(len(gsrp_articles))):
            try:
                url = gsrp_articles[item_id][1]
                soup = fetch_gsrp(url=url)
                content = soup.text
                pattern = "\n|\r|\t|\u3000|\x0a"
                content = "".join(
                    [sent.strip() for sent in re.split(pattern, content)]
                ).strip()
            except Exception as e:
                print(e)
                content = ""

            gsrp_articles[item_id] += (content,)

        article_results.update({kw: gsrp_articles})

        with open(article_output_filepath, "w", encoding="utf-8") as f:
            json.dump(article_results, f, ensure_ascii=False, indent=4)

    except:
        print(f"Keyword: {kw} broken. Keep on next.")
        continue
