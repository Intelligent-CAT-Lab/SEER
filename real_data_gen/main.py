import os
import csv
import pandas as pd
import sys

# def extract_name():
#     student_ids = os.listdir('./repositories')
#     student_id = student_ids[0]
#     f = open(f'./repositories/{student_id}/public-tests.tsv', 'r')
#     reader = csv.reader(f, delimiter='\t')
#     metadatas = []
#     metadatas += reader.__next__()
#     f.close()
#     f = open(f'./repositories/{student_id}/hidden-tests.tsv', 'r')
#     reader = csv.reader(f, delimiter='\t')
#     metadatas += reader.__next__()
#     f.close()
#     for i in range(len(metadatas)):
#         metadatas[i] = metadatas[i].replace('[', '').replace(']', '').replace('(', '').replace(')', '')
#     return metadatas


if __name__ == '__main__':
    # metadatas = extract_name()
    # for metadata in metadatas:
    #     os.system(f'python3 real_data_gen/read_results.py {metadata}')
    os.system('pwd')
    # os.system(f'python3 ./real_data_gen/read_result.py {metadata}')

    if len(sys.argv) > 1:
        df = pd.read_json('./real_data_gen/triplets.json')
        df = df.T
        projects = list(df['project'].unique())

        for project in projects:
            proj_data = df[df['project']==project]
            proj_data.to_json(f'./real_data_gen/triplets_{project}.json', orient='index', indent=4)

            os.system(f'python3 ./real_data_gen/create_vocab.py {project}')
            os.system(f'python3 ./real_data_gen/json_to_h5.py {project}')
            os.system(f'python3 ./learning/test.py --project {project}')
            os.system(f'python3 ./real_data_gen/analyze_results.py {project}')
        # print(metadata)
    else:
        os.system('python3 ./real_data_gen/create_vocab.py')
        os.system('python3 ./real_data_gen/json_to_h5.py')
        os.system('python3 ./learning/test.py')
        os.system('python3 ./real_data_gen/analyze_results.py')