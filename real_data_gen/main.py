import os
import pandas as pd
import sys
from tqdm import tqdm

from analyze_results import generate_results
from overall_project_metrics import calculate_overall_metrics, combine_project_data
from json_to_h5 import json_to_h5

if __name__ == "__main__":
    os.system("pwd")

    if len(sys.argv) == 1:
        json_to_h5(type="test", fold=0, model="JointEmbedder")
        os.system("python3 ./learning/test.py")
        generate_results(result_path=f"./real_data_gen/fold0/no_comments/")
    else:
        if sys.argv[1] == "project":
            comment_types = ["no_comments", "comments", "added_comments"]
            print(f"generating results for all projects...")
            for comment_type in comment_types:
                df = pd.read_json(f"./real_data_gen/triplets/{comment_type}/triplets.json", orient="index")
                projects = list(df["project"].unique())
                for project in tqdm(projects):
                    os.system(f"python3 ./learning/test.py --project {project} --comment_type {comment_type}")
                    generate_results(result_path=f"./real_data_gen/fold0/{comment_type}/{project}/")
                combine_project_data(projects=projects, comment_type=comment_type)
                calculate_overall_metrics(projects=projects, comment_type=comment_type)
                generate_results(result_path=f"./real_data_gen/fold0/")

        elif sys.argv[1] == "reproduction":
            for val in ["whole", "combined", "unseen"]:
                generate_results(
                    result_path="./real_data_gen/seer_data/",
                    classifier_filename=f"phase2_{val}.csv",
                    write_filename=f"results_{val}.txt",
                )
        else:
            print("Invalid argument.")
