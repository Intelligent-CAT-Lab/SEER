import sys
sys.path.append('../')

import torch 
import torch.utils.data as data
import tables as tb
import json
import numpy as np
from utils import PAD_ID, indexes2sent

class TestOracleDatasetPhase2(data.Dataset):
    def __init__(self, type, data_dir, f_code, max_code_len, f_test, max_test_len, f_label=None):
        self.type = type
        self.max_code_len=max_code_len
        self.max_test_len=max_test_len
        # 1. Initialize file path or list of file names.
        """read training data(list of int arrays) from a hdf5 file"""
        self.training=False
        print("loading data...")
        table_code = tb.open_file(data_dir + f_code)
        self.codes = table_code.get_node('/phrases')[:].astype(np.int64)
        self.idx_codes = table_code.get_node('/indices')[:]
        table_test = tb.open_file(data_dir + f_test)
        self.tests = table_test.get_node('/phrases')[:].astype(np.int64)
        self.idx_tests = table_test.get_node('/indices')[:]
        if f_label is not None:
            self.training=True
            table_label = tb.open_file(data_dir + f_label)
            self.labels = table_label.get_node('/labels')[:]
        
        assert self.idx_codes.shape[0] == self.idx_tests.shape[0]
        if f_label is not None:
            assert self.idx_codes.shape[0] == self.labels.shape[0]

        self.data_len = self.idx_codes.shape[0]
        print("{} entries".format(self.data_len))
        
    def pad_seq(self, seq, maxlen):
        if len(seq) < maxlen:
            seq=np.append(seq, [PAD_ID]*(maxlen-len(seq)))
        seq=seq[:maxlen]
        return seq
    
    def __getitem__(self, offset):          
        len, pos = self.idx_codes[offset]['length'], self.idx_codes[offset]['pos']
        code_len = min(int(len), self.max_code_len)
        code = self.codes[pos: pos + code_len]
        code = self.pad_seq(code, self.max_code_len)
        
        len, pos = self.idx_tests[offset]['length'], self.idx_tests[offset]['pos']
        test_len = min(int(len), self.max_test_len)
        test = self.tests[pos:pos + test_len]
        test = self.pad_seq(test, self.max_test_len)
        if self.type == 'JointEmbedder':
            test = self.pad_seq(test, max(self.max_code_len, self.max_test_len))
            code = self.pad_seq(code, max(self.max_code_len, self.max_test_len))

        if self.training:
            label = self.labels[offset]

            return code, test, label
        return code, test
        
    def __len__(self):
        return self.data_len


def load_dict(filename):
    return json.load(open(filename, "r"))


if __name__ == '__main__':
    input_dir = './phase2_dataset_final/'
    train_set = TestOracleDatasetPhase2('JointEmbedder', input_dir+'fold1/', 'code_train.h5', 723, 'test_train.h5', 1625, 'label_train.h5')
    train_data_loader = torch.utils.data.DataLoader(dataset=train_set, batch_size=1, shuffle=False, num_workers=1)
    valid_set = TestOracleDatasetPhase2('JointEmbedder', input_dir+'fold1/', 'code_valid.h5', 723, 'test_valid.h5', 1625, 'label_valid.h5')
    valid_data_loader = torch.utils.data.DataLoader(dataset=train_set, batch_size=1, shuffle=False, num_workers=1)
    test_set = TestOracleDatasetPhase2('JointEmbedder', input_dir, 'code_test.h5', 723, 'test_test.h5', 1625)
    test_data_loader = torch.utils.data.DataLoader(dataset=test_set, batch_size=1, shuffle=False, num_workers=1)
    code_vocab = load_dict(input_dir + 'vocab_phase2.json')
    test_vocab = load_dict(input_dir + 'vocab_phase2.json')

    print('============ Train Data ================')
    k = 0
    for batch in train_data_loader:
        batch = tuple([t.numpy() for t in batch])
        code, test, label = batch
        k += 1
        if k > 10: break
        print('-------------------------------')
        print('====> Code (FC/BC):', indexes2sent(code, code_vocab))
        print('====> Test Body:', indexes2sent(test, test_vocab))
        print('====> Label (P[1], F[0]):', label)

    print('============ Valid Data ================')
    k = 0
    for batch in valid_data_loader:
        batch = tuple([t.numpy() for t in batch])
        code, test, label = batch
        k += 1
        if k > 10: break
        print('-------------------------------')
        print('====> Code (FC/BC):', indexes2sent(code, code_vocab))
        print('====> Test Body:', indexes2sent(test, test_vocab))
        print('====> Label (P[1], F[0]):', label)

    print('\n\n============ Test Data ================')
    k=0
    for batch in test_data_loader:
        batch = tuple([t.numpy() for t in batch])
        code, test = batch
        k += 1
        if k > 10: break
        print('-------------------------------')
        print('====> Code (FC/BC):', indexes2sent(code, code_vocab))
        print('====> Test Body:', indexes2sent(test, test_vocab))
