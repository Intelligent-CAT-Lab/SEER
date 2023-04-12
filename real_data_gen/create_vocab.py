import json


def create_vocabulary(filtered_data, vocab_type):
    """
        this function creates vocabulary from the given data
    """
    vocabulary = {"<pad>": 0, "<s>": 1, "</s>": 2, "<unk>": 3}
    filtered_triplets = 'triplets.json'

    vocabulary = export_vocabulary(filtered_triplets, filtered_data, vocabulary, vocab_type)

    json_f = json.dumps(vocabulary, indent = 4)

    with open(f'{filtered_data}/vocab_{vocab_type}.json', 'w') as out_f:
        out_f.write(json_f)


def export_vocabulary(triplets, filtered_data, vocabulary, vocab_type):
    """
        this function exports vocabulary to json file
    """
    triplets = json.load(open(f'{filtered_data}/{triplets}', 'r'))
    print(f'length of triplets: {len(triplets.keys())}')
    for i in range(len(triplets.keys())):
        source_code_pos = triplets[str(i)]['C'].split()
        test_code_tokens = triplets[str(i)]['T'].split()

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

if __name__ == "__main__":
    filtered_data = './real_data_gen/'
    vocab_type = 'real_data'
    create_vocabulary(filtered_data, vocab_type)