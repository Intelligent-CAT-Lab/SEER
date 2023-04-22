import csv
import json
import sys
import pandas as pd

projects = sys.argv[1].split(sep='*')
# print(projects)

path = './real_data_gen/fold0'

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
results_dict = {}

for project in projects:
    results_project = {}
    reader = csv.reader(open(f"{path}/{project}/test_stats.csv", 'r'))
    num_rows = -1
    out_of_vocab = 0
    out_of_vocab_fail = 0
    out_of_vocab_pass = 0
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    recorded_rows = []
    flag = True
    for row in reader:
        num_rows += 1

        # row[0] is the prediction, Row[1] is the actual
        if row[0] == '-1':
            out_of_vocab += 1
            if (row[1] == '0'):
                out_of_vocab_fail += 1
            else:
                out_of_vocab_pass += 1    
        # predicted and actual pass
        elif row[1] == '1' and row[0] == '1':
            tp += 1
        # predicted fail and actual pass
        elif row[1] == '1' and row[0] == '0':
            fn += 1
        # predicted and actual fail
        elif row[1] == '0' and row[0] == '0':
            tn += 1
        # predicted pass and actual fail
        elif row[1] == '0' and row[0] == '1':
            fp += 1

    num_in_vocab = num_rows-out_of_vocab

    f1 = (2*tp)/(2*tp+fp+fn)
    pass_accuracy = (tp)/(tp+fn)
    fail_accuracy = (tn)/(tn+fp)
    accuracy = (tp+tn)/num_in_vocab

    pass_rate = (tp+fn)/num_in_vocab
    fail_rate = (tn+fp)/num_in_vocab

    results_project['accuracy'] = round(accuracy,4)
    results_project['f1'] = round(f1,4)
    results_project['pass_accuracy'] = round(pass_accuracy,4)
    results_project['fail_accuracy'] = round(fail_accuracy,4)

    results_project['pass_rate'] = round(pass_rate,4)
    results_project['fail_rate'] = round(fail_rate,4)


    results_dict[project] = results_project

# json_object = json.dumps(results_dict, indent=4)

# with open(f"{path}/project_stats.json", "w") as outfile:
#     outfile.write(json_object)

pd.DataFrame(results_dict).T.to_csv(f"{path}/project_stats.csv")