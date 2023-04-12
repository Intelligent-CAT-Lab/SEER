import utils
import os
import json


outputFile = f'./real_data_gen/method_set.json'
def build_method_set(student_id, outputFile):
    code_path = f'./repositories/{student_id}/src/main/java'
    method_set = {}
    for root, dirs, files in os.walk(code_path):
        for file in files:
            if file.endswith('.java'):
                f = open(os.path.join(root, file), 'r')
                lines = f.readlines()
                f.close()
                for line in lines:
                    if utils.is_method_sig(line):
                        method_name = line.split('(')[0].split(' ')[-1]
                        method_set[method_name] = f'{root}/{file}'
    with open(outputFile, 'w') as f:
        json.dump(method_set, f)
    return method_set

if __name__ == '__main__':
    build_method_set('bkwak', outputFile)
                