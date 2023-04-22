import csv
import os
import time
import sys

result_path = './real_data_gen/fold0/test_stats.csv' if len(sys.argv) < 2 else f'./real_data_gen/fold0/{sys.argv[1]}/test_stats.csv'

reader = csv.reader(open(result_path, 'r'))
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
    # if num_rows <= 68:
    #     recorded_rows.append(row)
    # f.write(recorded_rows[0])
    if row[0] == '-1':
        out_of_vocab += 1
        if (row[1] == '0'):
            out_of_vocab_fail += 1
        else:
            out_of_vocab_pass += 1
    elif row[1] == '1' and row[0] == '1':
        tp += 1
    elif row[1] == '1' and row[0] == '0':
        fp += 1
    elif row[1] == '0' and row[0] == '0':
        tn += 1
    elif row[1] == '0' and row[0] == '1':
        fn += 1
    # index = (num_rows-1) % 68
    # if num_rows> 68 and (row[0] != recorded_rows[index][0] or row[1] != recorded_rows[index][1]):
    #     f.write(recorded_rows[index])
    #     f.write(row)
    #     flag = False
    #     f.write(f'row {num_rows} is different')
    #     break

num_in_vocab = num_rows-out_of_vocab
format_r = lambda x: round(x,4)
# now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time()))
results_file = './real_data_gen/results.txt' if len(sys.argv) < 2 else f'./real_data_gen/fold0/{sys.argv[1]}/results.txt'
f = open(results_file, 'w') 

# f.write(f'{sys.argv[1]}\n')
f.write(f'num_rows: {num_rows}\n')
if out_of_vocab == 0:
    f.write(f'out_of_vocab: {out_of_vocab}\n')
else:
    f.write(f'out_of_vocab: {out_of_vocab} ({out_of_vocab_fail} fail = {format_r(out_of_vocab_fail/out_of_vocab)}, {out_of_vocab_pass} pass = {format_r(out_of_vocab_pass/out_of_vocab)})\n')
f.write(f'Percent Out of Vocab: {format_r((out_of_vocab)/num_rows)}\n\n')


f.write(f'Number in Pass Class: {tp+fp}, {format_r((tp+fp)/num_in_vocab)}\n')
f.write(f'tp: {tp}, {format_r(tp/num_in_vocab)}\n')
f.write(f'fp: {fp}, {format_r(fp/num_in_vocab)}\n')
f.write(f'pass accuracy: {tp}/{tp+fp} = {format_r((tp)/(tp+fp))}\n\n')

f.write(f'Number in Fail Class: {tn+fn}, {format_r((tn+fn)/num_in_vocab)}\n')
f.write(f'tn: {tn}, {format_r(tn/num_in_vocab)}\n')
f.write(f'fn: {fn}, {format_r(fn/num_in_vocab)}\n')
f.write(f'fail accuracy: {tn}/{tn+fn} = {format_r((tn)/(tn+fn))}\n\n')

f.write(f'accuracy: {tp+tn}/{num_rows-out_of_vocab} = {format_r((tp+tn)/num_in_vocab)}\n')
f.write(f'precision: {tp}/{tp+fp} = {format_r(tp/(tp+fp))}\n')
f.write(f'recall: {tp}/{tp+fn} = {format_r(tp/(tp+fn))}\n')
f.write(f'f1: {2*tp}/{2*tp+fp+fn} = {format_r((2*tp)/(2*tp+fp+fn))}\n\n')
f.close()