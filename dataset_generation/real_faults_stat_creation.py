import argparse
import csv
import json
import os

def get_bug_ids(project):
    out_path = "./bug_ids/" + project + ".txt"
    command = "defects4j query -p " + project + " -q bug.id > " + out_path
    os.system(command)
 
    with open(out_path) as f:
        bug_ids = f.readlines()
        bug_ids = list(map(lambda x: x.strip(), bug_ids))

    return bug_ids

def generate_stats(args):
    project_name = args.project_name
    path = "./real_faults_data/{}_filtered_tuples.json".format(project_name)
    with open(path, "r", encoding="ISO-8859-1", errors='ignore') as f:
        tuples = json.load(f)

    bug_ids = get_bug_ids(project_name)
    stats = dict()

    for bug_id in bug_ids:
        bug_id = str(bug_id)
        stats[bug_id] = dict()
        stats[bug_id]['BC # Passing Tests'] = 0
        stats[bug_id]['FC # Passing Tests'] = 0
        stats[bug_id]['BC # Failing Tests'] = 0
        stats[bug_id]['FC # Failing Tests'] = 0
        stats[bug_id]['# Label F'] = 0
        stats[bug_id]['# Label P'] = 0
        stats[bug_id]['BC # Dev Passing Tests'] = 0
        stats[bug_id]['FC # Dev Passing Tests'] = 0
        stats[bug_id]['BC # Dev Failing Tests'] = 0
        stats[bug_id]['FC # Dev Failing Tests'] = 0
        stats[bug_id]['BC # Randoop Passing Tests'] = 0
        stats[bug_id]['FC # Randoop Passing Tests'] = 0
        stats[bug_id]['BC # Randoop Failing Tests'] = 0
        stats[bug_id]['FC # Randoop Failing Tests'] = 0

    for _id in tuples:
        bug_id = tuples[_id]['bug_id']
        label = tuples[_id]['label']
        code_type = tuples[_id]['type']
        test_type = tuples[_id]['test_type']

        if label == 'P' and code_type == 'FC' and test_type == 'dev':
            stats[bug_id]['FC # Passing Tests']+=1
            stats[bug_id]['FC # Dev Passing Tests']+=1
        elif label == 'F' and code_type == 'FC' and test_type == 'dev':
            stats[bug_id]['FC # Failing Tests']+=1
            stats[bug_id]['FC # Dev Failing Tests']+=1
        elif label == 'P' and code_type == 'BC' and test_type == 'dev':
            stats[bug_id]['BC # Passing Tests']+=1
            stats[bug_id]['BC # Dev Passing Tests']+=1
        elif label == 'F' and code_type == 'BC' and test_type == 'dev':
            stats[bug_id]['BC # Failing Tests']+=1
            stats[bug_id]['BC # Dev Failing Tests']+=1
        elif label == 'P' and code_type == 'FC' and test_type == 'randoop':
            stats[bug_id]['FC # Passing Tests']+=1
            stats[bug_id]['FC # Randoop Passing Tests']+=1
        elif label == 'F' and code_type == 'FC' and test_type == 'randoop':
            stats[bug_id]['FC # Failing Tests']+=1
            stats[bug_id]['FC # Randoop Failing Tests']+=1
        elif label == 'P' and code_type == 'BC' and test_type == 'randoop':
            stats[bug_id]['BC # Passing Tests']+=1
            stats[bug_id]['BC # Randoop Passing Tests']+=1
        elif label == 'F' and code_type == 'BC' and test_type == 'randoop':
            stats[bug_id]['BC # Failing Tests']+=1
            stats[bug_id]['BC # Randoop Failing Tests']+=1



    field_names = ['Project ID', 'Bug ID', 'BC # Dev Failing Tests', 'BC # Dev Passing Tests', 'FC # Dev Failing Tests', 'FC # Dev Passing Tests',
                    'BC # Randoop Failing Tests', 'BC # Randoop Passing Tests', 'FC # Randoop Failing Tests', 'FC # Randoop Passing Tests',
                    '# Label F', '# Label P']

    rows = list()

    for bug_id in bug_ids:
        bug_id = str(bug_id)
        bc_dev_ft, bc_dev_pt = stats[bug_id]['BC # Dev Failing Tests'], stats[bug_id]['BC # Dev Passing Tests']
        bc_randoop_ft, bc_randoop_pt = stats[bug_id]['BC # Randoop Failing Tests'], stats[bug_id]['BC # Randoop Passing Tests']
        fc_dev_ft, fc_dev_pt = stats[bug_id]['FC # Dev Failing Tests'], stats[bug_id]['FC # Dev Passing Tests']
        fc_randoop_ft, fc_randoop_pt = stats[bug_id]['FC # Randoop Failing Tests'], stats[bug_id]['FC # Randoop Passing Tests']
        label_f = stats[bug_id]['BC # Failing Tests'] + stats[bug_id]['FC # Failing Tests']
        label_p = stats[bug_id]['BC # Passing Tests'] + stats[bug_id]['FC # Passing Tests']

        row = [project_name, bug_id, bc_dev_ft, bc_dev_pt, fc_dev_ft, fc_dev_pt,
                bc_randoop_ft, bc_randoop_pt, fc_randoop_ft, fc_randoop_pt, label_f, label_p]
        rows.append(row)
        

    with open('./real_fault_stats.csv', 'a') as f_object:
        csvwriter = csv.writer(f_object)
        csvwriter.writerow(field_names)
        csvwriter.writerows(rows)


def parse_args():
    parser = argparse.ArgumentParser(prog='creating real faults dataset stats')
    parser.add_argument('--project_name', type=str, default=None, help='project name that you want to get stats')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    generate_stats(args)
