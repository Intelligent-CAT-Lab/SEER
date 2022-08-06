"""
In this file, we will reproduce the results of all research questions
"""

import argparse
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd


def effective_generalization(filename):
    test_instances = {}
    with open(f'data/{filename}.json') as fr:
        test_instances = list(json.load(fr).items())

    y_true, y_pred = [], []
    with open(f'data/{filename}.txt') as fr:
        for line in fr.readlines()[1:]:
            line = line.split()
            y_true.append(int(line[1].strip()))
            y_pred.append(int(line[2].strip()))

    project_results = {}
    for i in range(len(test_instances)):
        project_results.setdefault(test_instances[i][1]['project'], {'true': [], 'pred': []})
        project_results[test_instances[i][1]['project']]['true'].append(y_true[i])
        project_results[test_instances[i][1]['project']]['pred'].append(y_pred[i])

    print("{:<20} {:<10} {:<10} {:<10} {:<10}".format('Subjects', 'TP (%)', 'FN (%)', 'TN (%)', 'FP (%)'))
    print()
    tps, fns, tns, fps = [0], [0], [0], [0]
    for project in project_results:
        tn, fp, fn, tp = confusion_matrix(project_results[project]['true'], project_results[project]['pred']).ravel()
        tpr = round(tp / (tp + fn) * 100, 2)
        fnr = round(fn / (tp + fn) * 100, 2)
        tnr = round(tn / (tn + fp) * 100, 2)
        fpr = round(fp / (tn + fp) * 100, 2)
        tps.append(tp)
        fns.append(fn)
        tns.append(tn)
        fps.append(fp)
        print("{:<20} {:<10} {:<10} {:<10} {:<10}".format(project, tpr, fnr, tnr, fpr))

    average_tpr = round(sum(tps) / sum(tps + fns) * 100, 2)
    average_fnr = round(sum(fns) / sum(tps + fns) * 100, 2)
    average_tnr = round(sum(tns) / sum(tns + fps) * 100, 2)
    average_fpr = round(sum(fps) / sum(tns + fps) * 100, 2)
    print('\n{:<20} {:<10} {:<10} {:<10} {:<10}'.format('Total', average_tpr, average_fnr, average_tnr, average_fpr))

    accuracy = round(accuracy_score(y_true, y_pred) * 100, 0)
    precision = round(precision_score(y_true, y_pred) * 100, 0)
    recall = round(recall_score(y_true, y_pred) * 100, 0)
    f1 = round(f1_score(y_true, y_pred) * 100, 0)

    print()
    print('{:<10}: {:<10}'.format('Accuracy', accuracy))
    print('{:<10}: {:<10}'.format('Precision', precision))
    print('{:<10}: {:<10}'.format('Recall', recall))
    print('{:<10}: {:<10}'.format('F1', f1))


def plot_attention_thresholds():
    with open('data/attention_threshold.txt') as fr:
        lines = fr.readlines()
        x = [float(line.split()[0]) for line in lines]
        y = [float(line.split()[1]) for line in lines]
        plt.plot(x, y, '-o', markersize=5)
        plt.ylim(0, 100)
        plt.xlabel('Attention Threshold')
        plt.ylabel('% Discovered Buggy Statement')
        plt.savefig('attention_threshold.png', dpi=300, bbox_inches='tight')


def plot_attention_weights(filename):
    attn_weights = ''
    with open(f'data/{filename}.txt') as fr:
        lines = fr.readlines()
        code_sequence = lines[6].strip().split()
        for line in lines[8:]:
            attn_weights += line

    twod_arr = []
    i = 0
    c = 0
    max_dim = len(code_sequence)
    while attn_weights[i] != '&':
        i += 1
        if attn_weights[i] == '[':
            intermed_arr = []
            while attn_weights[i+1] != ']':
                i += 1
                if attn_weights[i] == '\n': continue
                intermed_arr.append(attn_weights[i])
            raw_ = ''.join(intermed_arr).split()
            raw_ = [float(x) for x in raw_]

            twod_arr.append(raw_)

            c += 1

            if c == max_dim:
                break
    
    plt.figure(figsize=(7,7))
    plt.imshow(twod_arr, cmap='Blues')
    plt.xticks(range(max_dim), [str(i) for i in code_sequence], rotation=90, font='serif', fontsize=10)
    plt.yticks(range(max_dim), [str(i) for i in code_sequence], font='serif', fontsize=10)
    plt.savefig(f'attn_weights_{filename}.png', dpi=300, bbox_inches='tight')


def parse_embeddings():
    points = {'BC': [], 'FC': []}
    with open('data/embeddings.txt') as f:
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
    plt.savefig('fig_embeddings_lda.png', dpi=300, bbox_inches='tight')


def main(args):
    if args.RQ == 1:
        effective_generalization('phase2_whole')
    elif args.RQ == 2:
        effective_generalization('phase2_unseen')
    elif args.RQ == 3:
        if args.subsec == 'attn_weights':
            plot_attention_weights('test1522')
            plot_attention_weights('test2988')
        elif args.subsec == 'attn_threshold':
            plot_attention_thresholds()
        elif args.subsec == 'embeddings':
            plot_embeddings()


def parse_args():
    parser = argparse.ArgumentParser("reproduce results of research questions")
    parser.add_argument('--RQ', type=int, default=1, help='the research question number to reproduce')
    parser.add_argument('--subsec', type=str, default='attn_weights', help='the subsection for RQ3')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
