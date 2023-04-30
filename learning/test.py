import sys
sys.path.append('./')
# import os
# os.environ['CUDA_LAUNCH_BLOCKING'] = "1"

import json
import time
import torch
import argparse
from data_loader_phase2 import TestOracleDatasetPhase2
import configs, models
from tqdm import tqdm
from csv import DictWriter

def load_dict(filename):
    return json.load(open(filename, "r"))


def test(args):
    if args.project == '':
        data_path = args.data_path + args.comment_type + '/'
    else:
        data_path = args.data_path + args.comment_type + '/' + args.project + '/'

    test_set = TestOracleDatasetPhase2(args.model, data_path, 'code_test.h5', 1624, 'test_test.h5', 1624, 'label_test.h5')
    data_loader = torch.utils.data.DataLoader(dataset=test_set, batch_size=1, shuffle=False, num_workers=1)

    device = torch.device(f"cuda:{args.gpu_id}" if torch.cuda.is_available() else "cpu")
    config=getattr(configs, 'configs')()

    model = getattr(models, args.model)(config)
    if args.reload_from>0:
        ckpt_path = f'./output/epoch_{args.reload_from}_fold_{args.fold}.h5'
        model.load_state_dict(torch.load(ckpt_path, map_location=device))
        print('reloaded model')
    
    model = model.to(device)
    model.eval()
    predictions, actuals = [], []
    elapsed_times = []
    failing_tensor_dict = {}
    k = 0
    for batch in data_loader:
        start_time = time.time()
        code, test, y_true = [tensor.to(device) for tensor in batch]
        y_true = y_true.float().cpu()
        actuals.append(int(y_true[0]))
        try:
            with torch.no_grad():
                out = model(code, test, "", phase=2)
                out = torch.squeeze(out, 1)
                y_pred = torch.argmax(out, dim=1)
                y_pred = y_pred.cpu()
                predictions.append(int(y_pred[0]))
        except:
            predictions.append(-1)
            temp_dict = {
                'C': code,
                'T': test
            }
            failing_tensor_dict[k] = temp_dict
            k += 1

    if len(failing_tensor_dict) > 0:
        json_object = json.dumps(failing_tensor_dict, indent=4)
        with open(f"{data_path}failing_tensors{args.project}.json", "w") as outfile:
            outfile.write(json_object)
            

    elapsed_time = time.time() - start_time
    elapsed_times.append(elapsed_time)
    start_time = time.time()

    with open(f'./{data_path}/test_stats.csv', 'w') as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=['Predicted Label', 'Actual Label'])
        dictwriter_object.writerow({'Predicted Label': 'Predicted Label', 'Actual Label': 'Actual Label'})
        for i in range(len(predictions)):
            dictwriter_object.writerow({'Predicted Label': predictions[i], 'Actual Label': actuals[i]})
        f_object.close()

    print(f'Average time per batch (size=1): {sum(elapsed_times)/len(elapsed_times)}')


def parse_args():
    parser = argparse.ArgumentParser("Test the model on test dataset")
    parser.add_argument('--data_path', type=str, default='real_data_gen/fold0/', help='location of the data corpus')
    parser.add_argument('--model', type=str, default='JointEmbedder', help='model name')
    parser.add_argument('-d', '--dataset', type=str, default='TestOracleInferencePhase2', help='dataset')
    parser.add_argument('-t', '--timestamp', type=str,default='2023', help='time stamp')
    parser.add_argument('-g', '--gpu_id', type=int, default=0, help='GPU ID')
    parser.add_argument('--fold', type=int, default=1, help='fold to test from')
    parser.add_argument('--reload_from', type=int, default=29, help='step to reload from')
    parser.add_argument('--project', type=str, default='', help='project name')
    parser.add_argument('--comment_type', type=str, default='no_comments', help='Whether or not comments are included. Options: no_comments, added_comments, comments')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    test(args)
