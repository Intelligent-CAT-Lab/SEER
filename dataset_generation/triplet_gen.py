import sys
sys.path.append('../')

import argparse
from configs import configs
import os
import json
from csv import DictWriter


def generate_triplets(args):
    config = configs()
    projects = config['projects']

    if args.project_name != 'all':
        projects = [args.project_name]

    os.system("mkdir data bug_ids")
    os.system("mkdir data/tuples data/triplets")

    export_stats('PROJECT', 'BUG_ID', 'TOTAL TUPLES (with empty Cs)', 'EMPTY RATE', 
                 'TOTAL TUPLES (without empty Cs)', 'TOTAL TEST SUIT SIZE',
                 'PASSING TESTS FC', 'FAILING TESTS FC', 'PASSING TESTS BC', 'FAILING TESTS BC', 'TOTAL TRIGGERING')

    for project in projects:
        bug_ids = export_project_bugs(project)
        export_tuples_triplets(project, bug_ids)


def export_project_bugs(project):
    out_path = "./bug_ids/" + project + ".txt"
    command = "defects4j query -p " + project + " -q bug.id > " + out_path
    os.system(command)

    with open(out_path) as f:
        bug_ids = f.readlines()
        bug_ids = list(map(lambda x: x.strip(), bug_ids))

    return bug_ids


def export_tuples_triplets(project, bug_ids):
    counter = 0
    project_tuples = {}
    project_triplets = {}

    for bug_id in bug_ids:
        directory = "./projects/{}/{}/output/".format(project, bug_id)
        directory_files = os.listdir(directory)
        local_tuples = [f for f in os.listdir("./projects/{}/{}/output/".format(project, bug_id)) if os.path.isfile(directory + f)]

        temp = {}
        for loc_tuple in local_tuples: 
            local_tuples_loc = "./projects/{}/{}/output/{}".format(project, bug_id, loc_tuple)
            with open(local_tuples_loc, "r", encoding="ISO-8859-1", errors='ignore') as f:
                temp = json.load(f)
        
            found_methods_loc = "./projects/{}/{}/output/modified_classes/{}/foundMethods.txt".format(project, bug_id, loc_tuple.split("_")[0])
            try:
                with open(found_methods_loc, "r", encoding="ISO-8859-1", errors='ignore') as f:
                    found_methods = f.readlines()
                    found_methods = list(map(lambda x: x.strip(), found_methods))
            except:
                continue

            temp, empty_rate, total_tuples_wo_c, total_test_suit, pt_fc, ft_fc, pt_bc, ft_bc, total_triggering = process_tuples(temp, found_methods)
            export_stats(project, bug_id, len(temp), empty_rate, total_tuples_wo_c, total_test_suit, pt_fc, ft_fc, pt_bc, ft_bc, total_triggering)

            for tuple_id in temp:
                project_tuples[counter] = temp[tuple_id]
                project_triplets[counter] = {'code': temp[tuple_id]['code'], 
                                            'test_code': temp[tuple_id]['test_code'],
                                            'label': temp[tuple_id]['label']}
                counter += 1

    global_tuples = json.dumps(project_tuples, indent = 4)
    global_triplets = json.dumps(project_triplets, indent = 4)

    with open("./data/tuples/{}.json".format(project), "w") as out_f:
        out_f.write(global_tuples)

    with open("./data/triplets/{}.json".format(project), "w") as out_f:
        out_f.write(global_triplets)


def process_tuples(tuples, found_methods):
    stats = {}
    duplicate_ids = []
    total_empty = 0
    pt_bc, pt_fc, ft_bc, ft_fc, total_triggering = 0, 0, 0, 0, 0

    for _id in tuples:
        method_name = ""
        stats.setdefault(tuples[_id]['test_name'], {})
        stats[tuples[_id]['test_name']].setdefault(tuples[_id]['code'], [])
        if len(stats[tuples[_id]['test_name']][tuples[_id]['code']]) > 0:
            duplicate_ids.append(_id)
            continue
        stats[tuples[_id]['test_name']][tuples[_id]['code']].append(_id)
        
        test_code = tuples[_id]['test_code']
        if test_code:
            if any(method in test_code for method in found_methods):
                total_triggering+=1

        if tuples[_id]['code'] == '':
            total_empty += 1

        if tuples[_id]['type'] == 'FC' and tuples[_id]['label'] == 'P':
            pt_fc += 1
        elif tuples[_id]['type'] == 'FC' and tuples[_id]['label'] == 'F':
            ft_fc += 1
        elif tuples[_id]['type'] == 'BC' and tuples[_id]['label'] == 'P':
            pt_bc += 1
        elif tuples[_id]['type'] == 'BC' and tuples[_id]['label'] == 'F':
            ft_bc += 1

    for _id in duplicate_ids:
        tuples.pop(_id)

    try:
        empty_rate = total_empty / len(tuples)
    except ZeroDivisionError:
        empty_rate = 0

    total_tuples_wo_c = (1 - empty_rate) * len(tuples)
    total_test_suit = len(stats)

    return tuples, empty_rate, total_tuples_wo_c, total_test_suit, pt_fc, ft_fc, pt_bc, ft_bc, total_triggering


def export_stats(project, bug_id, total_tuples, empty_rate, total_tuples_wo_c, total_test_suit, pt_fc, ft_fc, pt_bc, ft_bc, total_triggering):
    field_names = [ 'PROJECT-BUG_ID', 'TOTAL TUPLES (with empty Cs)', 'EMPTY RATE', 
                    'TOTAL TUPLES (without empty Cs)', 'TOTAL TEST SUIT SIZE', 
                    'PASSING TESTS FC', 'FAILING TESTS FC', 'PASSING TESTS BC', 'FAILING TESTS BC', 'TOTAL TRIGGERING']

    dct = { 'PROJECT-BUG_ID': '{} - {}'.format(project, bug_id), 
            'TOTAL TUPLES (with empty Cs)': total_tuples, 
            'EMPTY RATE': empty_rate,
            'TOTAL TUPLES (without empty Cs)': total_tuples_wo_c,
            'TOTAL TEST SUIT SIZE': total_test_suit,
            'PASSING TESTS FC': pt_fc,
            'FAILING TESTS FC': ft_fc,
            'PASSING TESTS BC': pt_bc,
            'FAILING TESTS BC': ft_bc,
            'TOTAL TRIGGERING' : total_triggering
        }

    with open('./data/stats.csv', 'a') as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=field_names)    
        dictwriter_object.writerow(dct)
        f_object.close()


def parse_args():
    parser = argparse.ArgumentParser(prog='generating data triplets')
    parser.add_argument('--project_name', type=str, default='all', help='project you want to produce the triplets for')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    generate_triplets(args)
