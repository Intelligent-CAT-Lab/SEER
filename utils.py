import re
import os
import json
import sys
import tables as tb
import numpy as np
import random
from tqdm import tqdm

PAD_ID, SOS_ID, EOS_ID, UNK_ID = [0, 1, 2, 3]


def is_method_sig_format(statement):
    """
        this function determines whether the given statement is a method signature or not
    """
    tokens = statement.split()
    keywords = ['public', 'private', 'protected', 'static', 'final', 'native', 'synchronized', 
               'abstract', 'transient']

    if tokens == []:
        return 1

    if tokens[0] in keywords:
        curly_bracket = False
        opening_parenthesis = False
        closing_parenthesis = False

        for char in statement:
            if char == ';' or char == '=':
                return 1
            if char == '{':
                curly_bracket = True
                break
            elif char == '(':
                opening_parenthesis = True
            elif char == ')':
                closing_parenthesis = True
        
        if curly_bracket and opening_parenthesis and closing_parenthesis:
            return 2
        elif curly_bracket and not opening_parenthesis and not closing_parenthesis:
            return 1
        elif curly_bracket and not opening_parenthesis and closing_parenthesis:
            return 1
        else:
            return 3

    return 1


def is_method_sig(statement):
    """
        this function determines whether the given statement is a method signature or not
        params:
            statement (str): a single statement from source code
        return:
            bool: returns true if the statement is a method signature, and false otherwise
    """
    pattern = '(public|private|protected|static|final|native|synchronized|abstract|transient).*?\(.*?\).*?{'
    match = re.search(pattern, statement)

    if match is not None:
        return True
    return False


def extract_method_name(statement):
    """
        this function extracts the method name from the method signature
        params:
            statement (str): method signature
        return:
            method_name (str): method name extracted from method signature
    """
    assert is_method_sig(statement) == True
    method_name = statement.split('(')[0].split(' ')[-1]
    return method_name


def extract_method_names(location):
    """
        this function extracts all method names from a test class
    """
    method_names = []
    with open(location, "r", encoding="ISO-8859-1", errors='ignore') as fr:
        lines = fr.readlines()
        for i in range(len(lines)):
            line = lines[i].strip()
            st = i + 1
            while True:
                res = is_method_sig_format(line)
                if res == 1 or res == 2:
                    break
                elif res == 3:
                    line = line + " " + lines[st].strip()
                    st += 1
                    continue

            if not is_method_sig(line): continue
            method_name = extract_method_name(line)
            if not method_name.startswith('test'): continue
            method_names.append(method_name)

    return method_names


def mutant_compile_check(mutated_directory):
    """
        this function tests whether created mutant is compilable or not 
    """
    os.system("defects4j compile -w " + mutated_directory + " > ./compile_results.txt")

    with open("./compile_results.txt", "r", encoding="ISO-8859-1", errors='ignore') as f:
        compile_error = "Compilation failed"
        for line in f.readlines():
            line = line.strip()
            if compile_error in line:
                return False
        return True
    

def get_modified_method_names(project_name, bug_id):
    """
        this function returns list of modified method names 
    """
    #assuming that you are working on the directory you run the tuple_generator.py

    found_methods_dir = "./projects/" + project_name + "/" + str(bug_id) + "/output/modifiedClasses/foundMethods.txt"
    with open(found_methods_dir, "r", encoding="ISO-8859-1", errors='ignore') as f:
        found_methods = f.readlines()
        found_methods = list(map(lambda x: x.strip()), found_methods)
        return found_methods


def create_vocabulary(filtered_data, vocab_type):
    """
        this function creates vocabulary from the given data
    """
    vocabulary = {"<pad>": 0, "<s>": 1, "</s>": 2, "<unk>": 3}
    filtered_triplets = [x for x in os.listdir(filtered_data) if x.endswith(".json")]

    vocabulary = export_vocabulary(filtered_triplets, filtered_data, vocabulary, vocab_type)

    json_f = json.dumps(vocabulary, indent = 4)

    with open(f'{filtered_data}/vocab_{vocab_type}.json', 'w') as out_f:
        out_f.write(json_f)


def export_vocabulary(triplets, filtered_data, vocabulary, vocab_type):
    """
        this function exports vocabulary to json file
    """
    print(triplets[0])
    triplets = json.load(open(f'{filtered_data}/{triplets[0]}', 'r'))
    for triplet in triplets:
        for key in triplet.keys():
            source_code_pos = triplet[key]['C'].split()
            test_code_tokens = triplet[key]['T'].split()

        if vocab_type == 'code':                
            vocabulary = insert_to_vocabulary(source_code_pos, vocabulary)
        elif vocab_type == 'test':                
            vocabulary = insert_to_vocabulary(test_code_tokens, vocabulary)
        else:
            vocabulary = insert_to_vocabulary(source_code_pos, vocabulary)
            vocabulary = insert_to_vocabulary(test_code_tokens, vocabulary)

    return vocabulary


def insert_to_vocabulary(tokens, vocabulary):
    """
        this function inserts tokens to vocabulary
    """
    for token in tokens:
        stripped_token = token.strip().replace('\\', '')
        if stripped_token not in vocabulary:
            vocabulary[stripped_token] = len(vocabulary)    

    return vocabulary


class Particle(tb.IsDescription):
    length = tb.UInt32Col(shape=(), dflt=0, pos=0)
    pos = tb.UInt32Col(shape=(), dflt=0, pos=1)


def json_to_h5(type, fold, model):
    """
        this function converts json file to h5 file for phase 1 of model training.
        the logic stays the same for phase 2 as well with a few changes.
    """
    code_pos_h5 = tb.open_file(f"./data/fold{fold}/codepos_{type}.h5", mode="w")
    code_pos_diff_h5 = tb.open_file(f"./data/fold{fold}/codeposdiff_{type}.h5", mode="w")
    code_neg_h5 = tb.open_file(f"./data/fold{fold}/codeneg_{type}.h5", mode="w")
    code_neg_diff_h5 = tb.open_file(f"./data/fold{fold}/codenegdiff_{type}.h5", mode="w")
    test_h5 = tb.open_file(f"./data/fold{fold}/test_{type}.h5", mode="w")
    # label_h5 = tb.open_file(f"./phase2_dataset_final/fold{fold}/label_{type}.h5", mode="w")

    code_pos_table = code_pos_h5.create_table(code_pos_h5.root, 'indices', Particle, 'a table of indices and lengths')
    code_pos_e_array = code_pos_h5.create_earray(code_pos_h5.root, 'phrases', tb.Int64Atom(), (0,))

    code_posdiff_table = code_pos_diff_h5.create_table(code_pos_diff_h5.root, 'indices', Particle, 'a table of indices and lengths')
    code_posdiff_e_array = code_pos_diff_h5.create_earray(code_pos_diff_h5.root, 'phrases', tb.Int64Atom(), (0,))

    code_neg_table = code_neg_h5.create_table(code_neg_h5.root, 'indices', Particle, 'a table of indices and lengths')
    code_neg_e_array = code_neg_h5.create_earray(code_neg_h5.root, 'phrases', tb.Int64Atom(), (0,))

    code_negdiff_table = code_neg_diff_h5.create_table(code_neg_diff_h5.root, 'indices', Particle, 'a table of indices and lengths')
    code_negdiff_e_array = code_neg_diff_h5.create_earray(code_neg_diff_h5.root, 'phrases', tb.Int64Atom(), (0,))

    test_table = test_h5.create_table(test_h5.root, 'indices', Particle, 'a table of indices and lengths')
    test_e_array = test_h5.create_earray(test_h5.root, 'phrases', tb.Int64Atom(), (0,))

    # label_e_array = label_h5.create_earray(label_h5.root, 'labels', tb.Int8Atom(), (0,))

    if model == 'JointEmbedder':
        with open('./data/vocab_all.json') as fr:
            vocab_code = json.load(fr)
            vocab_test = vocab_code
    else:
        with open('./data/vocab_code.json') as fr:
            vocab_code = json.load(fr)

        with open('./data/vocab_test.json') as fr:
            vocab_test = json.load(fr)

    if type == 'test':
        with open(f'./data/{type}.json', "r", encoding="ISO-8859-1", errors='ignore') as fr:
            tuples = json.load(fr)
    else:
        with open(f'./data/fold{fold}/{type}{fold}.json', "r", encoding="ISO-8859-1", errors='ignore') as fr:
            tuples = json.load(fr)

    code_positive_curr_pos = 0
    code_positive_diff_curr_pos = 0
    code_negative_curr_pos = 0
    code_negative_diff_curr_pos = 0
    test_curr_pos = 0
    
    pbar = tqdm(tuples)
    c = 0
    for _id in pbar:
        c += 1
        pbar.set_description('Processing {}'.format(c))
        code_pos = tuples[_id]['C+'].split()
        code_pos_diff = [x.strip() for x in ' '.join(tuples[_id]['diff_C+']).split()]
        code_neg = tuples[_id]['C-'].split()
        code_neg_diff = [x.strip() for x in ' '.join(tuples[_id]['diff_C-']).split()]
        test_code = tuples[_id]['T'].split()
        # label = tuples[_id]['label']

        particle = test_table.row
        particle['length'] = len(test_code)
        particle['pos'] = test_curr_pos
        particle.append()

        for token in test_code:
            token = token.strip().replace('\\', '')
            test_e_array.append(np.array([vocab_test[token]]))
        
        test_curr_pos += len(test_code)

        particle = code_pos_table.row
        particle['length'] = len(code_pos)
        particle['pos'] = code_positive_curr_pos
        particle.append()

        for token in code_pos:
            token = token.strip().replace('\\', '')            
            code_pos_e_array.append(np.array([vocab_code[token]]))
        
        code_positive_curr_pos += len(code_pos)

        particle = code_posdiff_table.row
        particle['length'] = len(code_pos_diff)
        particle['pos'] = code_positive_diff_curr_pos
        particle.append()

        for token in code_pos_diff:
            token = token.strip().replace('\\', '')            
            code_posdiff_e_array.append(np.array([vocab_code[token]]))
        
        code_positive_diff_curr_pos += len(code_pos_diff)

        particle = code_neg_table.row
        particle['length'] = len(code_neg)
        particle['pos'] = code_negative_curr_pos
        particle.append()

        for token in code_neg:
            token = token.strip().replace('\\', '')            
            code_neg_e_array.append(np.array([vocab_code[token]]))
        
        code_negative_curr_pos += len(code_neg)

        particle = code_negdiff_table.row
        particle['length'] = len(code_neg_diff)
        particle['pos'] = code_negative_diff_curr_pos
        particle.append()

        for token in code_neg_diff:
            token = token.strip().replace('\\', '')            
            code_negdiff_e_array.append(np.array([vocab_code[token]]))
        
        code_negative_diff_curr_pos += len(code_neg_diff)

        # if label == 'P':
        #     label_e_array.append(np.array([1]))
        # else:
        #     label_e_array.append(np.array([0]))
        
        code_pos_table.flush()
        code_neg_table.flush()
        test_table.flush()

    code_pos_table.close()
    code_neg_table.close()
    test_table.close()


def get_max_len(dataset_dir):
    """
        this function is used to get the max length of code and test in the dataset.
        the max length is used to pad the code and test to the same length.
    """
    triplets = [dataset_dir + '/phase2.json']
    global_max_code_pos = 0
    global_max_code_neg = 0
    global_max_test = 0
    code_pos = ''
    code_neg = ''
    test = ''

    for processed_f in triplets:
        json_file = {}
        with open(processed_f) as fr:
            json_file = json.load(fr)

        for tuple_id in json_file:
            curr_code_pos = json_file[tuple_id]['C+'].split()
            curr_code_neg = json_file[tuple_id]['C-'].split()
            curr_test = json_file[tuple_id]['T'].split()

            if len(curr_code_pos) > global_max_code_pos:
                code_pos = curr_code_pos
                global_max_code_pos = len(curr_code_pos)

            if len(curr_code_neg) > global_max_code_neg:
                code_neg = curr_code_neg
                global_max_code_neg = len(curr_code_neg)

            if len(curr_test) > global_max_test:
                test = curr_test
                global_max_test = len(curr_test)

    print("Max code pos size: ", global_max_code_pos)
    print("Max code neg size: ", global_max_code_neg)
    print("Max test size: ", global_max_test)


def sent2indexes(sentence, vocab, maxlen):
    '''sentence: a string or list of string
       return: a numpy array of word indices
    '''      
    def convert_sent(sent, vocab, maxlen):
        idxes = np.zeros(maxlen, dtype=np.int64)
        idxes.fill(PAD_ID)
        tokens = sent.split()
        idx_len = min(len(tokens), maxlen)
        for i in range(idx_len): idxes[i] = vocab.get(tokens[i], UNK_ID)
        return idxes, idx_len
    if type(sentence) is list:
        inds, lens = [], []
        for sent in sentence:
            idxes, idx_len = convert_sent(sent, vocab, maxlen)
            #idxes, idx_len = np.expand_dims(idxes, 0), np.array([idx_len])
            inds.append(idxes)
            lens.append(idx_len)
        return np.vstack(inds), np.vstack(lens)
    else:
        inds, lens = sent2indexes([sentence], vocab, maxlen)
        return inds[0], lens[0]


def indexes2sent(indexes, vocab, ignore_tok=PAD_ID):
    '''indexes: numpy array'''
    def revert_sent(indexes, ivocab, ignore_tok=PAD_ID):
        indexes=filter(lambda i: i!=ignore_tok, indexes)
        toks, length = [], 0        
        for idx in indexes:
            toks.append(ivocab.get(idx, '<unk>'))
            length+=1
            if idx == EOS_ID:
                break
        return ' '.join(toks), length
    
    ivocab = {v: k for k, v in vocab.items()}
    if indexes.ndim==1:# one sentence
        return revert_sent(indexes, ivocab, ignore_tok)
    else:# dim>1
        sentences, lens =[], [] # a batch of sentences
        for inds in indexes:
            sentence, length = revert_sent(inds, ivocab, ignore_tok)
            sentences.append(sentence)
            lens.append(length)
        return sentences, lens


def train_valid_test_split(dataset_dir, test_rate, valid_rate):
    """
        this function is used to split the dataset into train, valid and test sets.
    """

    triplets = {}
    with open(dataset_dir + '/phase2.json', "r", encoding="ISO-8859-1", errors='ignore') as f:
        triplets = json.load(f)

    # counter = len(dataset)
    # test_keys = random.sample(list(dataset), int(float(test_rate) * counter))

    for i in range(1, 11):

        dataset = {}
        counter = 0

        for triplet_id in triplets:
            dataset[counter] = triplets[triplet_id]
            counter += 1

        test_val_dataset = {}
        for key in dataset.copy():
            if dataset[key]['project'] in ['Csv', 'Time', 'Mockito']:
                test_val_dataset[key] = dataset[key]
                dataset.pop(key)
                counter -= 1

        train_temp = dataset.copy()
        os.mkdir(f'./{dataset_dir}/fold{i}')

        # valid_keys = random.sample(list(train_temp), int(float(valid_rate) * counter))
        valid_dataset = {}
        valid_keys = random.sample(list(test_val_dataset), len(test_val_dataset) // 2)
        for key in valid_keys:
            valid_dataset[key] = test_val_dataset[key]
            test_val_dataset.pop(key)

        json_f = json.dumps(valid_dataset, indent = 4)
        with open(f'{dataset_dir}/fold{i}/valid{i}.json'.format(type), 'w') as out_f:
            out_f.write(json_f)

        json_f = json.dumps(train_temp, indent = 4)
        with open(f'{dataset_dir}/fold{i}/train{i}.json'.format(type), 'w') as out_f:
            out_f.write(json_f)

        json_f = json.dumps(test_val_dataset, indent = 4)
        with open(f'{dataset_dir}/fold{i}/test{i}.json'.format(type), 'w') as out_f:
            out_f.write(json_f)


def filter_asserts():
    """
        this function is used to filter the assert statements in the dataset.
    """
    data = {}
    with open('phase2.json') as fr:
        data = json.load(fr)

    pbar = tqdm(data)
    for key in pbar:
        pbar.set_description(f'processing {key}')
        test = data[key]['T']
        
        intervals = []
        for i in range(len(test)):
            if test[i:i+len('org.junit.Assert')] == 'org.junit.Assert':
                c=i
                paranthese_count = 0
                while (test[c] != ';' or paranthese_count != 0) and c < len(test)-1:
                    if test[c] == '(' and test[c:c+len('(#document')] != '(#document' and test[c:c+len('(:lt')] != '(:lt':
                        paranthese_count += 1
                    elif test[c] == ')':
                        paranthese_count -= 1

                    c+=1

                    if test[c:c+len('org.junit.Assert')] == 'org.junit.Assert':
                        c -= 1
                        break
                    
                    if test[c] == '}':
                        c -= 1
                        break
                
                intervals.append((test[i:c+1], ''))

            if test[i:i+len('assert')].lower() == 'assert':
                c=i
                paranthese_count = 0
                while (test[c] != ';' or paranthese_count != 0) and c < len(test)-1:
                    if test[c] == '(':
                        paranthese_count += 1
                    elif test[c] == ')':
                        paranthese_count -= 1

                    c+=1

                intervals.append((test[i:c+1], ''))

    for r in intervals:
        test = test.replace(*r)

    test = ' '.join(test.split())
    data[key]['T'] = test

    with open('phase2_no_asserts.json', 'w') as fw:
        json.dump(data, fw, indent=4)


if __name__ == '__main__':

    if sys.argv[1] == 'create_vocabulary':
        create_vocabulary('./real_data_gen/', sys.argv[2])

    elif sys.argv[1] == 'json_to_h5':
        json_to_h5(sys.argv[2], sys.argv[3], sys.argv[4])

    elif sys.argv[1] == 'get_max_len':
        get_max_len(sys.argv[2])

    elif sys.argv[1] == 'train_valid_test_split':
        train_valid_test_split(sys.argv[2], sys.argv[3], sys.argv[4])

    elif sys.argv[1] == 'filter_asserts':
        filter_asserts()