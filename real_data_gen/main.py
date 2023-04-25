import os
import pandas as pd
import sys

if __name__ == '__main__':
    os.system('pwd')

    if len(sys.argv) > 1:
        # df = pd.read_json('./real_data_gen/triplets.json')
        # df = df.T
        # projects = list(df['project'].unique())
        projects = ['commons-imaging-1.0-alpha3-src', 'spark', 'commons-lang3-3.12.0-src', 'http-request', 'commons-geometry-1.0-src', 'springside4', 'commons-jexl3-3.2.1-src', 'joda-time', 'async-http-client', 'JSON-java', 'bcel-6.5.0-src', 'commons-weaver-2.0-src', 'commons-numbers-1.0-src', 'commons-collections4-4.4-src', 'jsoup', 'commons-jcs3-3.1-src', 'commons-validator-1.7', 'commons-net-3.8.0', 'commons-beanutils-1.9.4', 'commons-pool2-2.11.1-src', 'commons-rng-1.4-src', 'commons-configuration2-2.8.0-src', 'commons-vfs-2.9.0', 'scribejava', 'commons-dbutils-1.7']

        for project in projects:
            #proj_data = df[df['project']==project]
            #proj_data.to_json(f'./real_data_gen/triplets_{project}.json', orient='index', indent=4)
            #os.system(f'rm -rf ./real_data_gen/fold0/{project}')
            #os.system(f'mkdir ./real_data_gen/fold0/{project}')

            #os.system(f'python3 ./real_data_gen/create_vocab.py {project}')
            os.system(f'python3 ./real_data_gen/json_to_h5.py {project}')
            os.system(f'python3 ./learning/test.py --project {project}')
            os.system(f'python3 ./real_data_gen/analyze_results.py {project}')
        project_string = '*'.join(projects)
        os.system(f'python3 ./real_data_gen/overall_project_metrics.py {project_string}')
        os.system(f'python3 ./real_data_gen/analyze_results.py')
        
    else:
        #os.system('python3 ./real_data_gen/create_vocab.py')
        #os.system('python3 ./real_data_gen/json_to_h5.py')
        os.system('python3 ./learning/test.py')
        os.system('python3 ./real_data_gen/analyze_results.py')
