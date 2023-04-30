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
        os.system('python3 ./learning/test.py')
        generate_results(result_path=f"./real_data_gen/fold0/")
    else:
        if sys.argv[1] == "project":
            
            comment_types = ["no_comments", "comments", "added_comments"]
            # Expect this to take ~15 minutes to run
            # TODO: split into separate scripts
            for comment_type in comment_types:

                df = pd.read_json(f"./real_data_gen/triplets/{comment_type}/triplets.json", orient="index")
                projects = list(df["project"].unique())

                print(f"generating json and h5 files for all projects...")
                for project in tqdm(projects):
                    proj_data = df[df['project']==project]
                    proj_data.to_json(f'./real_data_gen/triplets/{comment_type}/triplets_{project}.json', orient='index', indent=4)
                    os.system(f'mkdir -p ./real_data_gen/fold0/{comment_type}/{project}')

                    json_to_h5(type="test", fold=0, model="JointEmbedder", project=project, comment_type=comment_type)
                print(f"generating results for all projects...")
            # for comment_type in comment_types:
            #     for project in tqdm(projects):
            #         os.system(f'python3 ./learning/test.py --project {project}')
            #         generate_results(result_path=f"./real_data_gen/fold0/{project}/")
            #     combine_project_data(projects=projects)
            #     calculate_overall_metrics(projects=projects)
            #     generate_results(result_path=f"./real_data_gen/fold0/")
        elif sys.argv[1] == "reproduction":
            for val in ["whole", "combined", "unseen"]:
                generate_results(
                    result_path="./real_data_gen/seer_data/",
                    classifier_filename=f"phase2_{val}.csv",
                    write_filename=f"results_{val}.txt",
                )
        else:
            print("Invalid argument.")
