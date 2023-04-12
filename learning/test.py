import sys
sys.path.append('../')

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
    test_set = TestOracleDatasetPhase2(args.model, args.data_path, 'code_test.h5', 1075, 'test_test.h5', 1625, 'label_test.h5')
    data_loader = torch.utils.data.DataLoader(dataset=test_set, batch_size=1, shuffle=False, num_workers=1)

    device = torch.device(f"cuda:{args.gpu_id}" if torch.cuda.is_available() else "cpu")
    config=getattr(configs, 'configs')()

    model = getattr(models, args.model)(config)
    if args.reload_from>0:
        # ckpt_path = f'./output/{args.model}/{args.dataset}/{args.timestamp}/models/epoch_{args.reload_from}_fold_{args.fold}.h5'
        ckpt_path = f'./output/epoch_{args.reload_from}_fold_{args.fold}.h5'
        model.load_state_dict(torch.load(ckpt_path, map_location=device))
        print('reloaded model')
    
    model = model.to(device)
    model.eval()
    predictions, actuals = [], []
    elapsed_times = []
    for batch in data_loader:
        start_time = time.time()
        code, test, y_true = [tensor.to(device) for tensor in batch]
        y_true = y_true.float().cpu()
        with torch.no_grad():
            out = model(code, test, "", phase=2)
            out = torch.squeeze(out, 1)
            y_pred = torch.argmax(out, dim=1)
            y_pred = y_pred.cpu()
            predictions.append(int(y_pred[0]))
            actuals.append(int(y_true[0]))

        elapsed_time = time.time() - start_time
        elapsed_times.append(elapsed_time)
        start_time = time.time()
    now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time()))
    with open(f'./{args.data_path}/{now}test_stats.csv', 'w') as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=['Predicted Label', 'Actual Label'])
        dictwriter_object.writerow({'Predicted Label': 'Predicted Label', 'Actual Label': 'Actual Label'})
        for i in range(len(predictions)):
            dictwriter_object.writerow({'Predicted Label': predictions[i], 'Actual Label': actuals[i]})
        f_object.close()

    with open(f'./{args.data_path}/test_stats.csv', 'w') as f_object:
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
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    test(args)
