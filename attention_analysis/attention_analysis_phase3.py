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
    pdfname = "./attn_phase3_no_try_except/attn_weights_images_phase3/attn_weights" + key + ".pdf" #used for phase3
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

    f = open('../real_data_gen/zip/phase3_no_try_except/phase3_no_try_except.json') #used for phase3
    data = json.load(f)

    for key in data.keys():

        try:
            code_seq = data[key]['C'].strip()

            # computes the attention
            with torch.no_grad():
                seq = sent2indexes(code_seq, vocab, 1625)
                indices = seq[0][:seq[1][0]]
                index_seq = torch.tensor([indices]).to(device)
                embeddings = model.encoder.pos_encoder(model.encoder.encoder(index_seq))
                attn_output, attn_output_weights = model.encoder.transformer_encoder.layers[0].self_attn(embeddings, embeddings, embeddings)

            
            filename = "./attn_phase3_no_try_except/attn_weights_matrices_phase3/test" + key + ".txt" #used for phase3

            # used for documenting text matrices
            with open(filename, 'w') as file:
                file.write(key + "\n")
                file.write("Test: " + data[key]['T'] + "\n")
                file.write("Code: " + data[key]['C'] + "\n")
                file.write("[")
                for i in range(len(attn_output_weights)):
                    for j in range(len(attn_output_weights.numpy()[i])):
                        file.write(str(attn_output_weights.numpy()[i][j]))
                        if(j != len(attn_output_weights.numpy()[i])-1):
                            file.write("\n")
                file.write("]")
                print("written:", key)
            # with open(filename, 'a') as file:
            #     indexes = []
            #     print(attn_output_weights.numpy()[0])
            #     for i in range(len(attn_output_weights)):
            #         # file.write(str(attn_output_weights[i]))
            #         print(type(attn_output_weights[i]))
            #         for j in range(len(attn_output_weights[i])):
            #             max = -1
            #             highest_attn = ""
            #             if[attn_output_weights[i][j]>max]:
            #                 max = attn_output_weights[i][j]
            #                 temp = data[key]['C'].split()
            #                 highest_attn = temp[j]
            #                 indexes.append(highest_attn)
                # print("Indexes:", indexes)
                # file.write("\n" + highest_attn)



            plot_attn_weights(attn_output_weights, code_seq, key) # used for plotting heat map of matrices
        except:
            print("Could not create mapping:", key)

        

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
