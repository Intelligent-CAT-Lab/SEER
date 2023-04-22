import os
import pandas as pd
import sys

if __name__ == '__main__':
    os.system('pwd')

    if len(sys.argv) > 1:
        df = pd.read_json('./real_data_gen/triplets.json')
        df = df.T
        projects = list(df['project'].unique())

        for project in projects:
            #proj_data = df[df['project']==project]
            #proj_data.to_json(f'./real_data_gen/triplets_{project}.json', orient='index', indent=4)
            #os.system(f'rm -rf ./real_data_gen/fold0/{project}')
            #os.system(f'mkdir ./real_data_gen/fold0/{project}')

            #os.system(f'python3 ./real_data_gen/create_vocab.py {project}')
            #os.system(f'python3 ./real_data_gen/json_to_h5.py {project}')
            os.system(f'python3 ./learning/test.py --project {project}')
            os.system(f'python3 ./real_data_gen/analyze_results.py {project}')
        project_string = '*'.join(projects)
        os.system(f'python3 ./real_data_gen/overall_project_metrics.py {project_string}')
        os.system(f'python3 ./real_data_gen/analyze_results.py')
        
    else:
        os.system('python3 ./real_data_gen/create_vocab.py')
        os.system('python3 ./real_data_gen/json_to_h5.py')
        os.system('python3 ./learning/test.py')
        os.system('python3 ./real_data_gen/analyze_results.py')
