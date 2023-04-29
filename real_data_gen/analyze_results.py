import csv


def generate_results(
    result_path="./real_data_gen/fold0/",
    classifier_filename="test_stats.csv",
    write_filename="results.txt",
):
    reader = csv.reader(open(result_path + classifier_filename, "r"))
    num_rows = -1
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for row in reader:
        num_rows += 1

        # row[0] is the prediction, Row[1] is the actual
        # predicted and actual pass
        if row[1] == "1" and row[0] == "1":
            tp += 1
        # predicted fail and actual pass
        elif row[1] == "1" and row[0] == "0":
            fn += 1
        # predicted and actual fail
        elif row[1] == "0" and row[0] == "0":
            tn += 1
        # predicted pass and actual fail
        elif row[1] == "0" and row[0] == "1":
            fp += 1

    num_in_vocab = num_rows
    format_r = lambda x: round(x, 4)
    results_file = result_path + write_filename

    f = open(results_file, "w")

    f.write(f"num_rows: {num_rows}\n")

    f.write(f"Number in Pass Class: {tp+fn}, {format_r((tp+fn)/num_in_vocab)}\n")
    f.write(f"tp: {tp}, {format_r(tp/num_in_vocab)}\n")
    f.write(f"fp: {fp}, {format_r(fp/num_in_vocab)}\n")
    f.write(f"pass accuracy: {tp}/{tp+fn} = {format_r((tp)/(tp+fn))}\n\n")

    f.write(f"Number in Fail Class: {tn+fp}, {format_r((tn+fp)/num_in_vocab)}\n")
    f.write(f"tn: {tn}, {format_r(tn/num_in_vocab)}\n")
    f.write(f"fn: {fn}, {format_r(fn/num_in_vocab)}\n")
    f.write(f"fail accuracy: {tn}/{tn+fp} = {format_r((tn)/(tn+fp))}\n\n")

    f.write(f"accuracy: {tp+tn}/{num_rows} = {format_r((tp+tn)/num_in_vocab)}\n")
    f.write(f"precision: {tp}/{tp+fp} = {format_r(tp/(tp+fp))}\n")
    f.write(f"recall: {tp}/{tp+fn} = {format_r(tp/(tp+fn))}\n")
    f.write(f"f1: {2*tp}/{2*tp+fp+fn} = {format_r((2*tp)/(2*tp+fp+fn))}\n\n")
    f.close()
