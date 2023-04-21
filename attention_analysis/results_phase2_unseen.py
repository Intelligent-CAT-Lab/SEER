# Creating the mapping of keys to test_numbers
# import json
#
# results = open('../scripts/data/phase2_unseen.txt', 'r')
# dict_entries = open('../scripts/data/phase2_unseen.json', 'r')
# phase2 = json.load(dict_entries)
# mapping = open('results_phase2_unseen_mapping.txt', 'a')
# results_lines = results.readlines()
# count = 1
# for key in phase2.keys():
#     mapping.write(key + "\t" + results_lines[count])
#     count += 1
#
# mapping.close()
# dict_entries.close()
# results.close()


# Dividing up the results of phase2_unseen into categories of P/P, F/F, P/F, F/P
results = open('results_phase2_unseen_mapping.txt', 'r')

passed = open('./phase2_results/phase2_unseen_both_passed.txt', 'a')
failed = open('./phase2_results/phase2_unseen_both_failed.txt', 'a')
predict_failed = open('./phase2_results/phase2_unseen_pred_fail.txt', 'a')
predict_passed = open('./phase2_results/phase2_unseen_pred_pass.txt', 'a')

for l in results.readlines():
    words = l.split()
    if words[2] == '1' and words[3] == '1':
        passed.write(l)
    elif words[2] == '0' and words[3] == '0':
        failed.write(l)
    elif words[2] == '1' and words[3] == '0':
        predict_failed.write(l)
    elif words[2] == '0' and words[3] == '1':
        predict_passed.write(l)

predict_passed.close()
predict_failed.close()
failed.close()
passed.close()

results.close()
