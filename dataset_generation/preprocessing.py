import json
import argparse
import os
import shutil
import re
from tqdm import tqdm


def preprocess_data(args):
    dataset_names = []

    # checking dataset name
    if args.dataset_name == 'all':
        dataset_names = os.listdir(args.data_path)
    else:
        dataset_names.append(args.dataset_name)

    # checking if output dir exists
    if os.path.isdir(args.output_dir):
        user_choice = input('directory name {} already exists. continuing will overwrite the directory. do you want to continue [y or n]: '.format(args.output_dir))
        if user_choice in ['n', 'N']:
            print('aborting data preprocessing')
            return
        else:
            shutil.rmtree(os.path.join(os.getcwd(), args.output_dir))

    os.mkdir(args.output_dir)

    pbar = tqdm(dataset_names)
    for dataset_name in pbar:
        pbar.set_description('Processing {}'.format(dataset_name))
        dataset = read_dataset(args.data_path, dataset_name)
        dataset = clean_code(dataset)
        dataset = remove_duplicates(dataset, dataset_name)
        dataset = check_coverage(dataset)
        write_dataset(args.output_dir, dataset_name, dataset)


def read_dataset(data_path, dataset_name):
    dataset = {}
    with open('{}/{}'.format(data_path, dataset_name)) as json_read:
        dataset = json.load(json_read)
    return dataset


def write_dataset(output_dir, dataset_name, dataset):
    json_f = json.dumps(dataset, indent = 4)

    with open('{}/processed_{}'.format(output_dir, dataset_name), 'w') as out_f:
        out_f.write(json_f)


def clean_code(dataset):
    #if you do not copy, it will cause runtime error since the dictionary size is changing
    for tuple_id in dataset.copy():
        source_code_pos = dataset[tuple_id]['C+']
        source_code_neg = dataset[tuple_id]['C-']
        test_code = dataset[tuple_id]['T']
        dataset[tuple_id]['C+'] = filter_comments(source_code_pos)
        dataset[tuple_id]['C-'] = filter_comments(source_code_neg)
        dataset[tuple_id]['T'] = filter_comments(test_code)

        diff_cp = []
        diff_cn = []
        for i in range(len(dataset[tuple_id]['diff_C+'])):
            difference_pos = dataset[tuple_id]['diff_C+'][i]
            difference_neg = dataset[tuple_id]['diff_C-'][i]
            filtered_pos = filter_comments(difference_pos).strip()
            filtered_neg = filter_comments(difference_neg).strip()

            if filtered_pos == '' and filtered_neg == '':
                continue

            diff_cp.append(filtered_pos)
            diff_cn.append(filtered_neg)

        dataset[tuple_id]['diff_C+'] = diff_cp        
        dataset[tuple_id]['diff_C-'] = diff_cn

    return dataset


def filter_comments(code):
    cleaned_code = re.sub('//.*?\\n', '', code)   # removing single-line comments
    cleaned_code = cleaned_code.replace('\n', '') # removing new line char
    cleaned_code = re.sub('/\*.*?\*/', '', cleaned_code)  # removing multi-line comments
    return cleaned_code


def remove_duplicates(dataset, dataset_name):
    stats = {}
    duplicate_ids = []
    for _id in dataset:
        key = dataset[_id]['T'] + dataset_name
        stats.setdefault(key, {})
        stats[key].setdefault(dataset[_id]['C+']+dataset[_id]['C-'], [])
        if len(stats[key][dataset[_id]['C+']+dataset[_id]['C-']]) > 0:
            duplicate_ids.append(_id)
            continue
        stats[key][dataset[_id]['C+']+dataset[_id]['C-']].append(_id)

    for _id in duplicate_ids:
        dataset.pop(_id)

    return dataset


def check_coverage(dataset):
    """
        this function is used to check the coverage of a code by test.
    """
    counter = 0
    filtered_dataset = {}
    for id_ in dataset:
        code_p = dataset[id_]['C+'].split()
        dataset[id_]['C+'] = ' '.join([x.strip() for x in code_p])
        code_n = dataset[id_]['C-'].split()
        dataset[id_]['C-'] = ' '.join([x.strip() for x in code_n])
        test = dataset[id_]['T'].split()
        dataset[id_]['T'] = ' '.join([x.strip() for x in test])
        code_p = dataset[id_]['C+']
        code_p = dataset[id_]['C-']
        test = dataset[id_]['T']
        method_name = code_p.split('(')[0].split(' ')[-1]

        code_method = method_name.strip() + '('
        if code_method in test:
            filtered_dataset[str(counter)] = dataset[id_]
            counter += 1

    return filtered_dataset


def parse_args():
    parser = argparse.ArgumentParser(prog='preprocessing data')
    parser.add_argument('--data_path', type=str, default='triplets', help='location of the raw data')
    parser.add_argument('--output_dir', type=str, default='preprocessed_data', help='location of the preprocessed data')
    parser.add_argument('--dataset_name', type=str, default='all', help='name of the dataset (with extension, i.e., json) to be processed')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    preprocess_data(args)
