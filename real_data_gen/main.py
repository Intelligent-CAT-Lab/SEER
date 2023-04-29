import os
import pandas as pd
import sys

sys.path.append("./")
from analyze_results import generate_results
from overall_project_metrics import calculate_overall_metrics, combine_project_data

if __name__ == "__main__":
    os.system("pwd")

    if len(sys.argv) == 1:
        # os.system('python3 ./real_data_gen/json_to_h5.py')
        # os.system('python3 ./learning/test.py')
        generate_results(result_path=f"./real_data_gen/fold0/")
        # os.system('python3 ./real_data_gen/analyze_results.py')
    else:
        if sys.argv[1] == "project":

            df = pd.read_json("./real_data_gen/triplets/triplets.json", orient="index")
            projects = list(df["project"].unique())
            # projects = ['commons-imaging-1.0-alpha3-src', 'spark', 'commons-lang3-3.12.0-src', 'http-request', 'commons-geometry-1.0-src', 'springside4', 'commons-jexl3-3.2.1-src', 'joda-time', 'async-http-client', 'JSON-java', 'bcel-6.5.0-src', 'commons-weaver-2.0-src', 'commons-numbers-1.0-src', 'commons-collections4-4.4-src', 'jsoup', 'commons-jcs3-3.1-src', 'commons-validator-1.7', 'commons-net-3.8.0', 'commons-beanutils-1.9.4', 'commons-pool2-2.11.1-src', 'commons-rng-1.4-src', 'commons-configuration2-2.8.0-src', 'commons-vfs-2.9.0', 'scribejava', 'commons-dbutils-1.7']

            for project in projects:
                # proj_data = df[df['project']==project]
                # proj_data.to_json(f'./real_data_gen/triplets/triplets_{project}.json', orient='index', indent=4)
                # os.system(f'rm -rf ./real_data_gen/fold0/{project}')
                # os.system(f'mkdir ./real_data_gen/fold0/{project}')

                # os.system(f'python3 ./real_data_gen/json_to_h5.py {project}')
                #     os.system(f'python3 ./learning/test.py --project {project}')
                generate_results(result_path=f"./real_data_gen/fold0/{project}/")
                # os.system(f'python3 ./real_data_gen/analyze_results.py {project}')
            # project_string = '*'.join(projects)
            combine_project_data(projects=projects)
            calculate_overall_metrics(projects=projects)
            # os.system(f'python3 ./real_data_gen/overall_project_metrics.py {project_string}')
            generate_results(result_path=f"./real_data_gen/fold0/")
        elif sys.argv[1] == "coin":
            generate_results(
                result_path="./real_data_gen/fold0/",
                classifier_filename="test_stats_coin.csv",
                write_filename="results_coin.txt",
            )
        elif sys.argv[1] == "vocab-analysis":
            thresholds = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
            for threshold in thresholds:
                string = "{:.2f}".format(threshold)[2:]
                generate_results(
                    result_path="./real_data_gen/vocab-analysis/",
                    classifier_filename=f"test_stats_{string}.csv",
                    write_filename=f"results_{string}.txt",
                )
        elif sys.argv[1] == "reproduction":
            generate_results(
                result_path="./scripts/data/",
                classifier_filename="phase2_combined.csv",
                write_filename="results_combined.txt",
            )
        else:
            print("Invalid argument.")
