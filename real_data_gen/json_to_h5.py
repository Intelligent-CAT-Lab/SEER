import json
import tables as tb
import numpy as np
from tqdm import tqdm
import sys


class Particle(tb.IsDescription):
    length = tb.UInt32Col(shape=(), dflt=0, pos=0)
    pos = tb.UInt32Col(shape=(), dflt=0, pos=1)


def json_to_h5(type, fold, model, project=''):
    """
        this function converts json file to h5 file for phase 1 of model training.
        the logic stays the same for phase 2 as well with a few changes.
    """
    if (project == ''):
        fold_path = f'./real_data_gen/fold{fold}'
    else:
        fold_path = f'./real_data_gen/fold{fold}/{project}'

    try:
        f = open(f"{fold_path}/code_{type}.h5", "x")
        f.close()
        f = open(f"{fold_path}/test_{type}.h5", "x")
        f.close()
        f = open(f"{fold_path}/label_{type}.h5", "x")
        f.close()
    except:
        pass

    code_h5 = tb.open_file(f"{fold_path}/code_{type}.h5", mode="w")
    test_h5 = tb.open_file(f"{fold_path}/test_{type}.h5", mode="w")
    label_h5 = tb.open_file(f"{fold_path}/label_{type}.h5", mode="w")

    code_table = code_h5.create_table(code_h5.root, 'indices', Particle, 'a table of indices and lengths')
    code_e_array = code_h5.create_earray(code_h5.root, 'phrases', tb.Int64Atom(), (0,))



    test_table = test_h5.create_table(test_h5.root, 'indices', Particle, 'a table of indices and lengths')
    test_e_array = test_h5.create_earray(test_h5.root, 'phrases', tb.Int64Atom(), (0,))

    label_e_array = label_h5.create_earray(label_h5.root, 'labels', tb.Int8Atom(), (0,))

    if model == 'JointEmbedder':
        vocab_path = './real_data_gen/vocab_real_data.json' if project == '' else f'./real_data_gen/vocab_{project}.json'
        with open(vocab_path) as fr:
            vocab_code = json.load(fr)
            vocab_test = vocab_code
    else:
        with open(vocab_path) as fr:
            vocab_code = json.load(fr)

        with open(vocab_path) as fr:
            vocab_test = json.load(fr)

    if type == 'test':
        triplets_path = './real_data_gen/triplets.json' if project == '' else f'./real_data_gen/triplets_{project}.json'
        with open(triplets_path, "r", encoding="ISO-8859-1", errors='ignore') as fr:
            tuples = json.load(fr)
    else:
        with open(f'{fold_path}/{type}{fold}.json', "r", encoding="ISO-8859-1", errors='ignore') as fr:
            tuples = json.load(fr)

    codeitive_curr_pos = 0
    test_curr_pos = 0
    
    pbar = tqdm(tuples)
    c = 0
    
    failure_cases = {}

    for _id in pbar:
        c += 1
        pbar.set_description('Processing {}'.format(c))
        code = tuples[_id]['C'].split()
        test_code = tuples[_id]['T'].split()
        label = tuples[_id]['label']
        project = tuples[_id]['project']

        particle = test_table.row
        particle['length'] = len(test_code)
        particle['pos'] = test_curr_pos
        particle.append()

        failure_cases[c-1] =  {"project": project,"label":label, "C_tokens_num": len(code), "T_tokens":len(test_code), "C_tokens_fail":0, "T_tokens_fail":0}

        # fail_bool = False
        for token in test_code:
            token = token.strip().replace('\\', '')
            try:
                test_e_array.append(np.array([vocab_test[token]]))
            except:
                test_e_array.append(np.array([0]))
                failure_cases[c-1]['T_tokens_fail'] += 1
                # fail_bool = True
                # continue

        # if fail_bool:
        #     continue
        test_curr_pos += len(test_code)

        particle = code_table.row
        particle['length'] = len(code)
        particle['pos'] = codeitive_curr_pos
        particle.append()

        for token in code:
            token = token.strip().replace('\\', '')   
            try:
                code_e_array.append(np.array([vocab_code[token]]))
            except:
                code_e_array.append(np.array([0]))
                failure_cases[c-1]['C_tokens_fail'] += 1
                # fail_bool = True
                # continue

        # if fail_bool:
        #     continue
        
        codeitive_curr_pos += len(code)


        if label == 'P':
            label_e_array.append(np.array([1]))
        else:
            label_e_array.append(np.array([0]))
        
        code_table.flush()
        test_table.flush()

    code_table.close()
    test_table.close()
    
    with open(f'{fold_path}/out-of-vocab.json', "w") as outfile:
        outfile.write(json.dumps(failure_cases, indent=4))

if __name__ == '__main__':
    json_to_h5('test', 0, 'JointEmbedder') if len(sys.argv) == 1 else json_to_h5('test', 0, 'JointEmbedder', sys.argv[1])