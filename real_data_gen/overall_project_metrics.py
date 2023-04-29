import csv
import json
import sys
import numpy as np
import pandas as pd
import random
from tqdm import tqdm

projects = ['commons-imaging-1.0-alpha3-src', 'spark', 'commons-lang3-3.12.0-src', 'http-request', 'commons-geometry-1.0-src', 'springside4', 'commons-jexl3-3.2.1-src', 'joda-time', 'async-http-client', 'JSON-java', 'bcel-6.5.0-src', 'commons-weaver-2.0-src', 'commons-numbers-1.0-src', 'commons-collections4-4.4-src', 'jsoup', 'commons-jcs3-3.1-src', 'commons-validator-1.7', 'commons-net-3.8.0', 'commons-beanutils-1.9.4', 'commons-pool2-2.11.1-src', 'commons-rng-1.4-src', 'commons-configuration2-2.8.0-src', 'commons-vfs-2.9.0', 'scribejava', 'commons-dbutils-1.7']
# Defining functions
calc_f1 = lambda df: np.round((2*df['tp'])/(2*df['tp']+df['fp']+df['fn']), 4)
calc_pass_accuracy = lambda df: np.round((df['tp'])/(df['tp']+df['fn']), 4)
calc_fail_accuracy = lambda df: np.round((df['tn'])/(df['tn']+df['fp']), 4)
calc_accuracy = lambda df: np.round((df['tp']+df['tn'])/df['N'], 4)
calc_pass_rate = lambda df: np.round((df['tp']+df['fn'])/df['N'], 4)
calc_fail_rate = lambda df: np.round((df['tn']+df['fp'])/df['N'], 4)

def combine_project_data(projects):
    path = './real_data_gen/fold0'

    # Combining all the test_stats.csv files into one for subsequent analysis
    open(f"{path}/test_stats.csv", 'w').close()

    with open(f"{path}/test_stats.csv", "ab") as fout:
        # First file:
        with open(f"{path}/{projects[0]}/test_stats.csv", "rb") as f:
            fout.writelines(f)

        # Now the rest:
        for project in projects[1:]:
            with open(f"{path}/{project}/test_stats.csv", "rb") as f:
                next(f) # Skip the header, portably
                fout.writelines(f)
                
def run_coin_flip_test(project_data, pass_rate):
    df = project_data.copy()
    num_rows = len(df)
    coin_accuracy = []
    coin_f1 = []

    iterations = int(np.ceil(10000/num_rows))

    for i in range(iterations):
        coin_simulation = [1 if (random.random() < pass_rate) else 0 for i in range(num_rows)]
        df['coin_simulation'] = coin_simulation
        coin_tp = 0
        coin_fn = 0
        coin_tn = 0
        coin_fp = 0

        for i in range(num_rows):

            # row[0] is the prediction, Row[1] is the actual
            # predicted and actual pass
            if df.loc[i, 'Actual Label'] == 1 and df.loc[i, 'coin_simulation'] == 1:
                coin_tp += 1
            # predicted fail and actual pass
            elif df.loc[i, 'Actual Label'] == 1 and df.loc[i, 'coin_simulation'] == 0:
                coin_fn += 1
            # predicted and actual fail
            elif df.loc[i, 'Actual Label'] == 0 and df.loc[i, 'coin_simulation'] == 0:
                coin_tn += 1
            # predicted pass and actual fail
            elif df.loc[i, 'Actual Label'] == 0 and df.loc[i, 'coin_simulation'] == 1:
                coin_fp += 1

        coin_accuracy.append((coin_tp+coin_tn)/num_rows)
        coin_f1.append((2*coin_tp)/(2*coin_tp+coin_fp+coin_fn))

    average_coin_accuracy = np.round(np.mean(coin_accuracy), 4)
    average_coin_f1 = np.round(np.mean(coin_f1), 4)
    return average_coin_accuracy, average_coin_f1

# Intaking data
# projects = sys.argv[1].split(sep='*')
# projects = '*'.join(projects).split(sep='*')

def generate_vocab_data(temp, threshold, project):
    columns_vocab_summary = ['project', 'total_C_tokens', 'total_C_fail', 'out_vocab_C_ratio', 'total_T_tokens', 'total_T_fail', 'out_vocab_T_ratio', 'out_vocab_combined_ratio']
    temp = temp[(temp['project']==project) & (temp['out_vocab_ratio'] <= threshold)]

    valid_ind = temp.reset_index().index.tolist()

    total_C_tokens = np.sum(temp['C_tokens'])
    total_T_tokens = np.sum(temp['T_tokens'])
    total_T_fail = np.sum(temp['T_tokens_fail'])
    total_C_fail = np.sum(temp['C_tokens_fail'])

    if (total_C_tokens + total_T_tokens) == 0:
        return None, None

    out_vocab_C_ratio = np.round(total_C_fail / total_C_tokens, 2)
    out_vocab_T_ratio = np.round(total_T_fail / total_T_tokens, 2)
    out_vocab_combined_ratio = np.round((total_T_fail + total_C_fail) / (total_C_tokens + total_T_tokens), 2)
    # print(f'Error with {project}')
    # print(f'total_C_tokens: {total_C_tokens}')
    # print(f'total_T_tokens: {total_T_tokens}')
    # print(f'total_T_fail: {total_T_fail}')
    # print(f'total_C_fail: {total_C_fail}')

    data = [project, total_C_tokens, total_C_fail, out_vocab_C_ratio, total_T_tokens, total_T_fail, out_vocab_T_ratio, out_vocab_combined_ratio]

    temp_df = pd.DataFrame(data).T
    temp_df.columns = columns_vocab_summary

    return temp_df, valid_ind

def generate_results_data(project, path, valid_ind):
    results_project = {}
    project_data = pd.read_csv(f"{path}/{project}/test_stats.csv")
    project_data = project_data.reindex(valid_ind)

    num_rows = len(project_data)
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for i in range(num_rows):

        # row[0] is the prediction, Row[1] is the actual
        # predicted and actual pass
        if project_data.loc[i, 'Actual Label'] == 1 and project_data.loc[i, 'Predicted Label'] == 1:
            tp += 1
        # predicted fail and actual pass
        elif project_data.loc[i, 'Actual Label'] == 1 and project_data.loc[i, 'Predicted Label'] == 0:
            fn += 1
        # predicted and actual fail
        elif project_data.loc[i, 'Actual Label'] == 0 and project_data.loc[i, 'Predicted Label'] == 0:
            tn += 1
        # predicted pass and actual fail
        elif project_data.loc[i, 'Actual Label'] == 0 and project_data.loc[i, 'Predicted Label'] == 1:
            fp += 1

    results_project['N'] = num_rows
    results_project['tp'] = tp
    results_project['fn'] = fn
    results_project['tn'] = tn
    results_project['fp'] = fp

    # Dataset stats  
    results_project['accuracy'] = calc_accuracy(results_project)
    results_project['f1'] = calc_f1(results_project)
    results_project['pass_accuracy'] = calc_pass_accuracy(results_project)
    results_project['fail_accuracy'] = calc_fail_accuracy(results_project)

    results_project['pass_rate'] = calc_pass_rate(results_project)
    results_project['fail_rate'] = calc_fail_rate(results_project)

    # Coin flip test    
    results_project['coin_accuracy'], results_project['coin_f1'] = run_coin_flip_test(project_data, results_project['pass_rate'])
    results_project['accuracy_improvement'] = np.round(results_project['accuracy'] - results_project['coin_accuracy'], 4)

    return results_project

def calculate_overall_metrics(projects=projects, thresholds = [1.0, .50, .25, .10, .05]):

    # project_count = len(projects)
    path = './real_data_gen/fold0'

    # Vocab analysis
    print('Creating final results for each threshold value...')
    vocab = pd.read_json(f'{path}/out-of-vocab.json', orient='index')
    vocab['out_vocab_ratio'] = np.round((vocab['C_tokens_fail'] + vocab['T_tokens_fail']) / (vocab['C_tokens'] + vocab['T_tokens']), 2)
    columns_vocab_summary = ['project', 'total_C_tokens', 'total_C_fail', 'out_vocab_C_ratio', 'total_T_tokens', 'total_T_fail', 'out_vocab_T_ratio', 'out_vocab_combined_ratio']

    for threshold in tqdm(thresholds):
        threshold_string = "{:.2f}".format(threshold).replace('.', '')[1:] if threshold != 1.0 else 'all'
        # Initialize data objects
        vocab_summary = pd.DataFrame(columns=columns_vocab_summary)
        results_dict = {}
        for project in tqdm(projects, leave=False):
            # Vocab analysis
            temp_df, valid_ind = generate_vocab_data(vocab, threshold, project)
            if temp_df is None:
                continue
            vocab_summary = pd.concat([vocab_summary, temp_df], ignore_index=True)
            # Results analysis
            results_project = generate_results_data(project, path, valid_ind)
            results_dict[project] = results_project

        vocab_summary.loc['all', 'project'] = 'all'
        vocab_summary.loc['all', 'total_C_tokens'] = np.sum(vocab_summary['total_C_tokens'])
        vocab_summary.loc['all', 'total_C_fail'] = np.sum(vocab_summary['total_C_fail'])
        vocab_summary.loc['all', 'out_vocab_C_ratio'] = np.round(vocab_summary.loc['all', 'total_C_fail'] / vocab_summary.loc['all', 'total_C_tokens'], 2)
        vocab_summary.loc['all', 'total_T_tokens'] = np.sum(vocab_summary['total_T_tokens'])
        vocab_summary.loc['all', 'total_T_fail'] = np.sum(vocab_summary['total_T_fail'])
        vocab_summary.loc['all', 'out_vocab_T_ratio'] = np.round(vocab_summary.loc['all', 'total_T_fail'] / vocab_summary.loc['all', 'total_T_tokens'], 2)
        vocab_summary.loc['all', 'out_vocab_combined_ratio'] = np.round((vocab_summary.loc['all', 'total_T_fail'] + vocab_summary.loc['all', 'total_C_fail']) / (vocab_summary.loc['all', 'total_C_tokens'] + vocab_summary.loc['all', 'total_T_tokens']), 2)


        sorting = pd.DataFrame(results_dict).T
        sorting.index.name = 'project'
        sorting = sorting.reset_index().merge(vocab_summary[['project','out_vocab_C_ratio','out_vocab_T_ratio', 'out_vocab_combined_ratio']], left_on='project', right_on='project', how='outer').set_index('project')
        sorting.sort_values(by=['accuracy_improvement'], ascending=False, inplace=True)

        # Adding totals
        sorting.loc['all', 'N'] = np.sum(sorting['N'])
        sorting.loc['all', 'tp'] = np.sum(sorting['tp'])
        sorting.loc['all', 'fn'] = np.sum(sorting['fn'])
        sorting.loc['all', 'tn'] = np.sum(sorting['tn'])
        sorting.loc['all', 'fp'] = np.sum(sorting['fp'])
        sorting.loc['all', 'accuracy'] = calc_accuracy(sorting.loc['all'])
        sorting.loc['all', 'f1'] = calc_f1(sorting.loc['all'])
        sorting.loc['all', 'pass_accuracy'] = calc_pass_accuracy(sorting.loc['all'])
        sorting.loc['all', 'fail_accuracy'] = calc_fail_accuracy(sorting.loc['all'])
        sorting.loc['all', 'pass_rate'] = calc_pass_rate(sorting.loc['all'])
        sorting.loc['all', 'fail_rate'] = calc_fail_rate(sorting.loc['all'])

        overall_results_df = pd.read_csv(f"{path}/test_stats.csv")
        sorting.loc['all', 'coin_accuracy'], sorting.loc['all', 'coin_f1'] = run_coin_flip_test(overall_results_df, sorting.loc['all', 'pass_rate'])
        sorting.loc['all', 'accuracy_improvement'] = np.round(sorting.loc['all', 'accuracy'] - sorting.loc['all', 'coin_accuracy'], 4)

        sorting = sorting.astype({'fn': 'int32', 'tn': 'int32', 'fp': 'int32', 'tp': 'int32', 'N': 'int32'})


        sorting.to_csv(f"{path}/project_stats_{threshold_string}.csv")