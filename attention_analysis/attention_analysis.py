import sys
sys.path.append('../')

import warnings
warnings.filterwarnings("ignore")

import sys
import json
import torch
import argparse
import matplotlib.pyplot as plt

import configs, models
from utils import sent2indexes


def load_dict(filename):
    return json.load(open(filename))


def plot_attn_weights(attn_output_weights, code_seq, key):
    code_seq = code_seq.split()
    plt.figure(figsize=(7,7))
    data = attn_output_weights.squeeze(0).detach().cpu().numpy()
    plt.imshow(data, cmap='Blues')
    plt.xticks(range(len(code_seq)), [str(i) for i in code_seq], rotation=90)
    plt.yticks(range(len(code_seq)), [str(i) for i in code_seq])
    plt.colorbar()
    pdfname = "./attn_weights_images/attn_weights" + key + ".pdf"
    plt.savefig(pdfname, format='pdf', dpi=300, bbox_inches='tight')
    plt.close('all')


def main(args):
    device = torch.device(f"cuda:{args.gpu_id}" if torch.cuda.is_available() else "cpu")
    config=getattr(configs, 'configs')()
    model = getattr(models, args.model)(config)

    if args.reload_from>0:
        ckpt_path = f'epoch_{args.reload_from}_fold_{args.fold_number}.h5'
        model.load_state_dict(torch.load(ckpt_path, map_location=device))
        print('reloaded model')
    
    model = model.to(device)
    model.eval()

    vocab = load_dict('vocab_phase2.json')

    f = open('../scripts/data/phase2_unseen.json')
    phase2 = json.load(f)

    for key in phase2.keys():

        #issue with "Fail to allocate bitmap" for 15163 -- 15163 does not have a pdf
        #if int(key) > 15163:
        #issue with "UnicodeEncodeError: 'charmap' codec can't encode character '\x82' in position 112: character maps to <undefined>" for 29895 -- 29895's txt isn't complete and the pdf dne
        #if int(key) > 29895:
        #issue with "UnicodeEncodeError: 'charmap' codec can't encode character '\x8f' in position 85: character maps to <undefined>" for 67980 -- 67980's txt isn't complete and the pdf dne
        #if int(key) > 67980:
        #issue with "UnicodeEncodeError: 'charmap' codec can't encode character '\x8f' in position 85: character maps to <undefined>" for 67981 -- 67981's txt isn't complete and the pdf dne
        #if int(key) > 67981:
        #issue with "UnicodeEncodeError: 'charmap' codec can't encode character '\x99' in position 227: character maps to <undefined>" for 68122 -- 68122's txt isn't complete and the pdf dne
        if int(key) > 68122:

            try:
                code_seq = phase2[key]['C'].strip()

                with torch.no_grad():
                    seq = sent2indexes(code_seq, vocab, 1625)
                    indices = seq[0][:seq[1][0]]
                    index_seq = torch.tensor([indices]).to(device)
                    embeddings = model.encoder.pos_encoder(model.encoder.encoder(index_seq))
                    attn_output, attn_output_weights = model.encoder.transformer_encoder.layers[0].self_attn(embeddings, embeddings, embeddings)

                filename = "./attn_weights_matrices/test" + key + ".txt"
                with open(filename, 'w') as file:
                    file.write(key + "\n")
                    file.write("Test: " + phase2[key]['T'] + "\n")
                    file.write("Code: " + phase2[key]['C'] + "\n")
                    for i in range(len(attn_output_weights)):
                        file.write(str(attn_output_weights[i]))

                plot_attn_weights(attn_output_weights, code_seq, key)
            except:
                print(key)

    f.close()


def parse_args():
    parser = argparse.ArgumentParser("Analyze attention weights of the model using heatmaps")
    parser.add_argument('--model', type=str, default='JointEmbedder', help='model name')
    parser.add_argument('--dataset', type=str, default='TestOracleInferencePhase2', help='dataset')
    parser.add_argument('--gpu_id', type=int, default=0, help='GPU ID')
    parser.add_argument('--fold_number', type=int, default=1, help='fold of the pretrained model')
    parser.add_argument('--reload_from', type=int, default=-1, help='epoch of the pretrained model')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args)
