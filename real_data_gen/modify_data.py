import pandas as pd
import os
import re
from tqdm import tqdm

folder_dir = "./toga_star"

colnames = ["dataset", "project", "bug_id", "C", "T", "docstring"]
df = pd.DataFrame(columns=colnames)
folder_names = os.listdir(folder_dir)

# Read project data
print("Reading project data...")
for project in tqdm(folder_names):
    project_path = os.path.join(folder_dir, project)
    temp_df = pd.read_csv(project_path + "/inputs.csv")
    temp_df.columns = ["C", "T", "docstring"]
    temp_df = temp_df.dropna()
    temp_df["dataset"] = "toga*"
    temp_df["project"] = project
    temp_df["bug_id"] = "-1"
    df = pd.concat([df, temp_df], ignore_index=True, axis=0)

df["label"] = "P"
df = df.drop("docstring", axis=1)
df["T"] = df.apply(lambda row: re.sub(r"\s*assert.*", "", row["T"]), axis=1)
for col in ["C", "T"]:
    df[col] = df[col].astype(str)
    # Remove comments
    df[col] = df.apply(lambda row: re.sub(r"\s*\/\/.*\n", "", row[col].strip()), axis=1)
    # Remove multiple spaces and line breaks
    df[col] = df.apply(lambda row: re.sub(r"\s\s*", " ", row[col].strip()), axis=1)

# REGEX
r_try = r"try\s*{"
r_fail = r"fail\([^;]*;\s*}"
r_except = r"catch\([^}]*\s*}"

try_except_regex = [r_try, r_fail, r_except]


print("Applying REGEX...")
for regex in tqdm(try_except_regex):
    df["label"] = df.apply(
        lambda row: "F" if (re.search(regex, row["T"]) != None) else row["label"],
        axis=1,
    )
    df["T"] = df.apply(lambda row: re.sub(regex, "", row["T"]), axis=1)

df.to_json("./real_data_gen/triplets/triplets.json", orient="index", indent=4)