import sys
sys.path.append('../')

import warnings
warnings.simplefilter('ignore')

import os
import random
import time
from datetime import datetime
import numpy as np
os.environ['NUMEXPR_MAX_THREADS'] = '32' #Number of maximum threads can be used
import argparse
random.seed(42)

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

import torch
import models, configs
from modules import get_cosine_schedule_with_warmup, EarlyStopping
from data_loader_phase1 import *

def save_model(model, ckpt_path):
    torch.save(model.state_dict(), ckpt_path)

def load_model(model, ckpt_path, to_device):
    assert os.path.exists(ckpt_path), f'Weights not found'
    model.load_state_dict(torch.load(ckpt_path, map_location=to_device))

def train(args):
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)
    device = torch.device(f"cuda:{args.gpu_id}" if torch.cuda.is_available() else "cpu") 

    config=getattr(configs, 'configs')()
    
    ###############################################################################
    # Load data
    ###############################################################################
    data_path = args.data_path

    train_dataset = eval(config['dataset_name'])(args.model, data_path, args.fold, config['codepos_train_dataset'], config['code_len'], config['codepos_diff_train'],
                    config['codeneg_train_dataset'], config['code_len'], config['codeneg_diff_train'], config['test_train_dataset'], config['test_len'])

    valid_dataset = eval(config['dataset_name'])(args.model, data_path, args.fold, config['codepos_valid_dataset'], config['code_len'], config['codepos_diff_valid'],
                    config['codeneg_valid_dataset'], config['code_len'], config['codeneg_diff_valid'], config['test_valid_dataset'], config['test_len'])

    # make output directory if it doesn't already exist
    os.makedirs(f'./output/{args.model}/{args.dataset}/{timestamp}/models', exist_ok=True)
    
    fh = logging.FileHandler(f"./output/{args.model}/{args.dataset}/{timestamp}/logs.txt")
                                    # create file handler which logs even debug messages
    logger.addHandler(fh)# add the handlers to the logger
        
    train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=config['batch_size'], 
                                                shuffle=True, drop_last=True, num_workers=1)

    valid_loader = torch.utils.data.DataLoader(dataset=valid_dataset, batch_size=config['batch_size'], 
                                                shuffle=True, drop_last=True, num_workers=1)

    ###############################################################################
    # Define Model
    ###############################################################################
    logger.info(f'Constructing Model ...')
    model = getattr(models, args.model)(config)#initialize the model

    if args.reload_from>0:
        ckpt = f'./output/{args.model}/{args.dataset}/{args.timestamp}/models/epoch{args.reload_from}_{args.fold_number}.h5'
        load_model(model, ckpt, device)    

    model.to(device)    
    
    ###############################################################################
    # Prepare the Optimizer
    ###############################################################################

    no_decay = ['bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
            {'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
            {'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
    ]    
    optimizer = torch.optim.AdamW(optimizer_grouped_parameters, lr=config['learning_rate'], eps=config['adam_epsilon'])        
    scheduler = get_cosine_schedule_with_warmup(
            optimizer, num_warmup_steps=config['warmup_steps'], 
            num_training_steps=len(train_loader)*config['nb_epoch'])

    criterion = torch.nn.MarginRankingLoss(margin=config['margin'])

    ###############################################################################
    # Training Process
    ###############################################################################
    ckpt_path = f'./output/{args.model}/{args.dataset}/{timestamp}/models/'
    early_stopping = EarlyStopping(patience=config['patience'], verbose=True, path=ckpt_path)

    ones = torch.ones([config['batch_size']]).to(device)
    n_iters = len(train_loader)
    for epoch in range(int(args.reload_from/n_iters)+1, config['nb_epoch']+1): 
        epoch_start_time = time.time()
        losses = []
        epoch_step_times = []
        for batch in train_loader:
            step_start_time = time.time()

            model.train()
            test, code_pos, code_neg, code_pos_diff, code_neg_diff = [tensor.to(device) for tensor in batch]
            anchor_sim = model(code_pos, test, code_pos_diff, phase=1, type='simple')
            neg_sim = model(code_neg, test, code_neg_diff, phase=1, type='simple')

            loss = criterion(anchor_sim, neg_sim, ones)

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
                
            optimizer.step()
            scheduler.step()

            losses.append(loss.item())
            
            time_elapsed_step = time.time() - step_start_time
            epoch_step_times.append(time_elapsed_step)                
            step_start_time = time.time()
        
        time_elapsed_epoch = time.time() - epoch_start_time
        logger.info('end_of_epoch=%d; avg_loss=%.5f; avg_step_time=%dms; total_epoch_time=%ds' % (epoch, np.mean(losses), np.mean(epoch_step_times) * 1000, time_elapsed_epoch))

        epoch_start_time = time.time()
        losses = []
        epoch_step_times = []

        mean_valid_loss = validate(valid_loader, model, device, criterion, ones)

        early_stopping(mean_valid_loss, model, epoch, args.fold, logger)
        
        if early_stopping.early_stop:
            print("Early stopping at epoch: %d" % epoch)
            break


def validate(data_loader, model, device, criterion, ones):
    model.eval()
    valid_losses = []
    for batch in data_loader:
        test, code_pos, code_neg, code_pos_diff, code_neg_diff = [tensor.to(device) for tensor in batch]
        anchor_sim = model(code_pos, test, code_pos_diff, phase=1, type='simple')
        neg_sim = model(code_neg, test, code_neg_diff, phase=1, type='simple')
        loss = criterion(anchor_sim, neg_sim, ones)
        valid_losses.append(loss.item())
    
    return np.mean(valid_losses)

def parse_args():
    parser = argparse.ArgumentParser("Train and Validate The Test Oracle Inference (Embedding) Model in Phase 1")
    parser.add_argument('--data_path', type=str, default='./phase1_dataset_final/', help='location of the data corpus')
    parser.add_argument('--model', type=str, default='JointEmbedder', help='model name: JointEmbeder, CodeTestEmbedder')
    parser.add_argument('--dataset', type=str, default='TestOracleInferencePhase1', help='name of dataset.java, python')
    parser.add_argument('--reload_from', type=int, default=-1, help='epoch to reload from')
    parser.add_argument('--fold_number', type=int, default=1, help='fold to reload from')
    parser.add_argument('--timestamp', type=int, default=1, help='timestamp to load from')
    parser.add_argument('--fold', type=int, default=1, help='fold to train on')   
    parser.add_argument('--gpu_id', type=int, default=0, help='GPU ID')
    parser.add_argument('--seed', type=int, default=1111, help='random seed')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    torch.backends.cudnn.benchmark = True # speed up training by using cudnn
    torch.backends.cudnn.deterministic = True # fix the random seed in cudnn
   
    train(args)
