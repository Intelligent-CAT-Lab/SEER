import pandas as pd
import os
import re
from tqdm import tqdm
tqdm.pandas()

def clean_text(df, remove_comments=True):
    for col in ["C", "T"]:
        df[col] = df[col].astype(str)
        # Remove comments
        if remove_comments:
            df[col] = df.progress_apply(lambda row: re.sub(r"\s*\/\/.*\n", "", row[col].strip()), axis=1)
        # Remove multiple spaces and line breaks
        df[col] = df.progress_apply(lambda row: re.sub(r"\s\s*", " ", row[col].strip()), axis=1)

    return df

def apply_regex(df):
    r_try = r"try\s*{"
    r_fail = r"fail\([^;]*;\s*}"
    r_except = r"catch\([^}]*\s*}"
    try_except_regex = [r_try, r_fail, r_except]

    for regex in tqdm(try_except_regex):
        df["label"] = df.apply(
            lambda row: "F" if (re.search(regex, row["T"]) != None) else row["label"],
            axis=1,
        )
        df["T"] = df.apply(lambda row: re.sub(regex, "", row["T"]), axis=1)

    return df


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

print("Cleaning text (0/6)...")
df_comments = clean_text(df, remove_comments=False)
print("Cleaning text (2/6)...")
df_no_comments = clean_text(df, remove_comments=True)

# REGEX
print("Applying REGEX...")
df_comments = apply_regex(df_comments)
df_no_comments = apply_regex(df_no_comments)

df_comments.to_json("./real_data_gen/triplets/triplets_comments.json", orient="index", indent=4)
df_no_comments.to_json("./real_data_gen/triplets/triplets_no_comments.json", orient="index", indent=4)

df_added_comments = df_no_comments.copy()
df_added_comments['T'] = df_no_comments.apply(lambda row: row['T'][:-1] + "// Undeclared exception!" + row['T'][-1:], axis=1)
df_added_comments.to_json("./real_data_gen/triplets/triplets_added_comments.json", orient="index", indent=4)
