import os
import pandas as pd


if __name__ == "__main__":
    data_rootpath = "../../forResearch/data/gcs/Crawling/"
    twse_securities_filepath = os.path.join(
        data_rootpath, "Financial/data/twse_securities_ids"
    )
    twse = pd.ExcelFile(twse_securities_filepath + ".xlsx")
    twse_sheet_names = twse.sheet_names
    shared_columns = ["有價證券代號及名稱", "category", "國際證券辨識號碼(ISIN Code)", "CFICode"]
    df_list = []
    for name in twse_sheet_names[:-3]:
        df = twse.parse(name)
        df.columns = [col.strip() for col in df.columns]
        df["category"] = name
        df_list.append(df[shared_columns])

    all_security_df = pd.concat(df_list, axis=0)
    all_security_df.columns = ["id_name", "category", "ISINCode", "CFICode"]
    all_security_df = all_security_df.dropna()
    all_security_df[["id", "name"]] = all_security_df["id_name"].str.split(
        "　", 1, expand=True
    )
    all_security_df = all_security_df.drop("id_name", axis=1)
    all_security_df = all_security_df[["id", "name", "category", "ISINCode", "CFICode"]]
    print(all_security_df.shape)
    print(all_security_df.head())
    print(all_security_df[["id", "name"]].drop_duplicates().shape)
    print(all_security_df["id"].unique().shape)
    all_security_df.to_csv(twse_securities_filepath + ".csv", index=False)
