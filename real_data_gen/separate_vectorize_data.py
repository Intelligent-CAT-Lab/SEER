import os
import pandas as pd
from tqdm import tqdm

from json_to_h5 import json_to_h5

if __name__ == "__main__":
    comment_types = ["no_comments", "comments", "added_comments"]
    # Expect this to take ~15 minutes to run
    for comment_type in tqdm(comment_types, desc="comment versions"):

        df = pd.read_json(f"./real_data_gen/triplets/{comment_type}/triplets.json", orient="index")
        projects = list(df["project"].unique())

        print(f"generating json and h5 files for all projects...")
        for project in tqdm(projects):
            proj_data = df[df["project"] == project]
            proj_data.to_json(
                f"./real_data_gen/triplets/{comment_type}/triplets_{project}.json",
                orient="index",
                indent=4,
            )
            os.system(f"mkdir -p ./real_data_gen/fold0/{comment_type}/{project}")

            json_to_h5(
                type="test",
                fold=0,
                model="JointEmbedder",
                project=project,
                comment_type=comment_type,
            )
