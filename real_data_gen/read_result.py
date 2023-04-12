import csv
import os
import json
import utils
from build_method_set import build_method_set
import time
import sys


def read_metadata(metadata):
    # split the string by '/'
    class_ids = []
    test_ids = []
    for ind in metadata:
        class_id = ind.split('/')[1]
        test_id = ind.split('/')[2]
        # remove '[', ']' and 'class:' in class_id
        class_id = class_id.split(':')[1][:-1]
        # remove '[', ']' and 'method:' in test_id
        test_id = test_id.split(':')[1][:-1]
        test_id = test_id.split('(')[0] + '('
        class_ids.append(class_id)
        test_ids.append(test_id)
    return class_ids, test_ids

def test_extract(student_id, class_id, test_id):
    """Extract the test from the data"""
    test = ''
    class_path = class_id.replace('.', '/') + '.java'
    f = open(f'{repo_path}/{student_id}/src/test/java/{class_path}', 'r')
    # extract the test code
    lines = f.readlines()
    f.close()
    for i in range(len(lines)):
        if '{' in lines[i] and test_id in lines[i]:
            for j in range(i, len(lines)-1):
                if lines[j].strip().startswith('@Tag'):
                    break
                if lines[j].strip().startswith('assert'):
                    continue
                test += lines[j]
            test = test.strip().replace('\n', ' ')
            test = ' '.join(test.split())
            return test

def method_extract(student_id, test):
    """extract all the method code the test invokes"""
    method_set = build_method_set(student_id, f'./real_data_gen/method_set.json')
    visited = []
    method = ''
    for token in test.split():
        if '(' not in token:
            continue
        token = token.split('(')[0].split('.')[-1]
        if token in method_set and token not in visited:
            visited.append(token)
            f = open(method_set[token], 'r')
            lines = f.readlines()
            f.close()
            for i in range(len(lines)):
                if utils.is_method_sig(lines[i]) and token in lines[i]:
                    method += lines[i]
                    for j in range(i+1, len(lines)-1):
                        if utils.is_method_sig(lines[j]):
                            break
                        method += lines[j]
                    # split method by the last '}'
                    method = method.rsplit('}', 1)[0] + '}'
                    break
    method = method.strip().replace('\n', ' ')
    method = ' '.join(method.split())
    return method


repo_path = './repositories'
student_ids = os.listdir(repo_path)
student_ids.remove('.DS_Store')
student_ids.remove('pyip')
methods = []
tests = []
labels = []
triplets = {}
accumulate = 0
if len(sys.argv) > 1:
    target_test = sys.argv[1]
else:
    target_test = None

for student_id in student_ids:
    for filename in ['public-tests.tsv', 'hidden-tests.tsv']:
        f = open(f'{repo_path}/{student_id}/{filename}', 'r')
        reader = csv.reader(f, delimiter='\t')
        metadata = reader.__next__()
        class_ids, test_ids = read_metadata(metadata)
        labels += reader.__next__()
        f.close()

        for i in range(len(class_ids)):
            if target_test is not None:
                if metadata[i].replace('[', '').replace(']', '').replace('(', '').replace(')', '') != target_test:
                    continue
            test = test_extract(student_id, class_ids[i], test_ids[i])
            tests.append(test)
            # print(class_ids[i])
            # print(test_ids[i])
            method = method_extract(student_id, test)
            # print(test)
            methods.append(method)
            triplets[str(accumulate)] = {}
            triplets[str(accumulate)]['dataset'] = "COMP 3021"
            triplets[str(accumulate)]['project'] = student_id
            triplets[str(accumulate)]['bug_id'] = metadata[i]
            triplets[str(accumulate)]['T'] = tests[accumulate]
            triplets[str(accumulate)]['C'] = methods[accumulate]
            triplets[str(accumulate)]['label'] = 'P' if labels[accumulate] == '1' else 'F'
            accumulate += 1

outputFile = f'./real_data_gen/triplets.json'
with open(outputFile, 'w') as f:
    json.dump(triplets, f, indent=4)

# for test_id in metadata:
#     triplets_separated = {}
#     for i in triplets:
#         if triplets[i]['bug_id'] == test_id:
#             triplets_separated[i] = triplets[i]
#     f = open(outputFile, 'w')
#     json.dump(triplets_separated, f, indent=4)
#     f.close()
#     os.system('python3 ./real_data_gen/create_vocab.py')
#     os.system('python3 ./real_data_gen/json_to_h5.py')
#     os.system('python3 ./learning/test.py')
#     os.system('python3 ./real_data_gen/analyze_results.py ' + test_id)
#     print('sleeping for 3 seconds...')
#     time.sleep(3)

