import argparse
import json
import torch
import random
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.insert(0, parent_dir)

torch.multiprocessing.set_sharing_strategy('file_system')
import configs, models
from data_loader_phase1 import TestOracleDatasetPhase1


def load_dict(filename):
    return json.load(open(filename))


def main(args):
    dataset = TestOracleDatasetPhase1(args.model, args.data_path, args.fold_number, 'codepos_train.h5', 604, 'codeposdiff_train.h5', 'codeneg_train.h5', 604, 'codenegdiff_train.h5', 'test_train.h5', 1625)
    data_loader = torch.utils.data.DataLoader(dataset=dataset, batch_size=1, shuffle=False, num_workers=1)
    bc_embedding, fc_embedding = get_embeddings(data_loader, args.pos_enc, args)
    apply_lda(bc_embedding, fc_embedding)
    plot_embeddings()


def get_embeddings(data_loader, pos_enc, args):
    device = torch.device(f"cuda:{args.gpu_id}" if torch.cuda.is_available() else "cpu")
    config=getattr(configs, 'configs')()
    model = getattr(models, args.model)(config)

    if args.reload_from > 0:
        ckpt_path = f'epoch_{args.reload_from}_fold_{args.fold_number}.h5'
        model.load_state_dict(torch.load(ckpt_path, map_location=device))
        print('reloaded model')
    
    model = model.to(device)   
    model.eval()

    bc_embedding, fc_embedding = [], []
    
    # sample 50% of the dataset for visualization due to memory constraints
    sampled_idx = random.sample(list(range(18736)), 18736 // 2)

    c = 0
    for batch in data_loader:
        if c not in sampled_idx:
            c += 1
            continue

        print('processing batch {}'.format(c))
        test, codepos, codeneg, codeposdiff, codenegdiff = [tensor.to(device) for tensor in batch]
        codepos_emb = model.encoder.encoder(codepos)
        codeneg_emb = model.encoder.encoder(codeneg)

        if pos_enc:
            codepos_emb = model.encoder.pos_encoder(codepos_emb)
            codeneg_emb = model.encoder.pos_encoder(codeneg_emb)

        codepos_emb = torch.squeeze(codepos_emb, 0).flatten()
        codeneg_emb = torch.squeeze(codeneg_emb, 0).flatten()

        bc_embedding.append(codeneg_emb.detach().cpu().numpy())
        fc_embedding.append(codepos_emb.detach().cpu().numpy())

        c += 1

    return bc_embedding, fc_embedding


def apply_lda(bc_embedding, fc_embedding):
    all_embs = np.array(bc_embedding + fc_embedding)
    y = np.array([1] * 9368 + [2] * 9368)
    clf = LinearDiscriminantAnalysis()
    embs = clf.fit_transform(all_embs, y)

    with open('embeddings.txt', 'w') as fw:
        fw.write("total bc_embeddings: {}\n".format(len(bc_embedding)))
        fw.write("total fc_embeddings: {}\n".format(len(fc_embedding)))

        counter = 1
        for sample in embs:
            fw.write("{} - {}\n".format(counter, sample))
            counter += 1


def parse_embeddings():
    points = {'BC': [], 'FC': []}
    with open('embeddings.txt') as f:
        lines = f.readlines()
        for i in range(2, len(lines)):
            line = lines[i].strip()
            line = line[line.find("[")+1:line.find("]")]
            point = [float(x) for x in line.split()]

            if 2 <= i <= 9370:
                points['BC'].append(point)
            elif 9371 <= i:
                points['FC'].append(point)

    return points


def plot_embeddings():
    points = parse_embeddings()
    embeddings = np.array([points['BC'] + points['FC']]).reshape(1, -1)

    bc = embeddings[0, :9368]
    fc = embeddings[0, 9368:]

    font_size = 16
    plt.figure(num = 3, figsize=(8, 6))

    s1 = pd.Series(bc)
    s2 = pd.Series(fc)
    s1.plot.kde(label='C-', color='#ffd966', linewidth=3)
    s2.plot.kde(label='C+', color='#6fa8dc', linewidth=3, linestyle='dotted')

    ellipse = matplotlib.patches.Ellipse((0.7, 0), 3, 0.2, color='#76DC6F', fill=False, linewidth=3)
    plt.gca().add_patch(ellipse)

    plt.xticks(fontsize=font_size, fontfamily='arial')
    plt.yticks(fontsize=font_size, fontfamily='arial')
    plt.ylabel('Distribution', fontsize=font_size, fontfamily='arial')
    plt.xlabel('Linear Discriminant Axis', fontsize=font_size, fontfamily='arial')
    plt.legend(loc='best', prop={'size': font_size, 'family': 'arial'})
    plt.savefig('fig_embeddings_lda.pdf', dpi=300, bbox_inches='tight')
    plt.show()


def parse_args():
    parser = argparse.ArgumentParser("Visualize Buggy and Fixed Code Embeddings")
    parser.add_argument('--data_path', type=str, default='./phase1_dataset_final/', help='location of the data corpus')
    parser.add_argument('--model', type=str, default='JointEmbedder', help='model name')
    parser.add_argument('--dataset', type=str, default='TestOracleInferencePhase1', help='dataset')
    parser.add_argument('--gpu_id', type=int, default=0, help='GPU ID')
    parser.add_argument('--reload_from', type=int, default=1, help='epoch to reload from')
    parser.add_argument('--fold_number', type=int, default=1, help='fold to visualize embeddings')
    parser.add_argument('--pos_enc', type=bool, default=False, help='include positional encodings')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
