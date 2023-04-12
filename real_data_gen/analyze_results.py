import csv
import os
import time
import sys

result_path = './real_data_gen/fold0/test_stats.csv'

reader = csv.reader(open(result_path, 'r'))
num_rows = -1
num_acc = 0
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
    if row[0] == '1' and row[1] == '1':
        tp += 1
    elif row[0] == '1' and row[1] == '0':
        fp += 1
    elif row[0] == '0' and row[1] == '0':
        tn += 1
    elif row[0] == '0' and row[1] == '1':
        fn += 1
    # index = (num_rows-1) % 68
    # if num_rows> 68 and (row[0] != recorded_rows[index][0] or row[1] != recorded_rows[index][1]):
    #     f.write(recorded_rows[index])
    #     f.write(row)
    #     flag = False
    #     f.write(f'row {num_rows} is different')
    #     break
now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time()))
f = open(f'./{now}real_data_gen/results.txt', 'a')
# f.write(f'{sys.argv[1]}\n')
f.write(f'num_rows: {num_rows}\n')
f.write(f'tp: {tp}\n')
f.write(f'fp: {fp}\n')
f.write(f'tn: {tn}\n')
f.write(f'fn: {fn}\n')
f.write(f'accuracy: {tp+tn}/{num_rows} = {round((tp+tn)/num_rows, 4)}\n')
f.write(f'precision: {tp}/{tp+fp} = {round(tp/(tp+fp), 4)}\n')
f.write(f'recall: {tp}/{tp+fn} = {round(tp/(tp+fn), 4)}\n\n')
f.close()