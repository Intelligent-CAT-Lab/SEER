import torch 
import torch.utils.data as data
import tables as tb
import json
import numpy as np
from utils import PAD_ID, indexes2sent


class TestOracleDatasetPhase1(data.Dataset):
    def __init__(self, type, data_dir, fold, f_code_pos, max_code_pos_len, f_code_pos_diff, f_code_neg, max_code_neg_len, f_code_neg_diff, f_test, max_test_len):
        self.type = type
        self.max_code_pos_len=max_code_pos_len
        self.max_code_neg_len=max_code_neg_len
        self.max_test_len=max_test_len
        # 1. Initialize file path or list of file names.
        """read training data(list of int arrays) from a hdf5 file"""
        print("loading data...")
        table_code_pos = tb.open_file(data_dir + f'fold{fold}/' + f_code_pos)
        self.codes_pos = table_code_pos.get_node('/phrases')[:].astype(np.int64)
        self.idx_codes_pos = table_code_pos.get_node('/indices')[:]

        table_code_pos_diff = tb.open_file(data_dir + f'fold{fold}/' + f_code_pos_diff)
        self.codes_pos_diff = table_code_pos_diff.get_node('/phrases')[:].astype(np.int64)
        self.idx_codes_pos_diff = table_code_pos_diff.get_node('/indices')[:]

        table_code_neg = tb.open_file(data_dir + f'fold{fold}/' + f_code_neg)
        self.codes_neg = table_code_neg.get_node('/phrases')[:].astype(np.int64)
        self.idx_codes_neg = table_code_neg.get_node('/indices')[:]

        table_code_neg_diff = tb.open_file(data_dir + f'fold{fold}/' + f_code_neg_diff)
        self.codes_neg_diff = table_code_neg_diff.get_node('/phrases')[:].astype(np.int64)
        self.idx_codes_neg_diff = table_code_neg_diff.get_node('/indices')[:]

        table_test = tb.open_file(data_dir + f'fold{fold}/' + f_test)
        self.tests = table_test.get_node('/phrases')[:].astype(np.int64)
        self.idx_tests = table_test.get_node('/indices')[:]
        
        assert self.idx_codes_pos.shape[0] == self.idx_tests.shape[0]
        assert self.idx_codes_neg.shape[0] == self.idx_tests.shape[0]

        self.data_len = self.idx_codes_pos.shape[0]
        print("{} entries".format(self.data_len))
        
    def pad_seq(self, seq, maxlen):
        if len(seq) < maxlen:
            seq=np.append(seq, [PAD_ID]*(maxlen-len(seq)))
        seq=seq[:maxlen]
        return seq
    
    def __getitem__(self, offset):          
        len, pos = self.idx_codes_pos[offset]['length'], self.idx_codes_pos[offset]['pos']
        code_pos_len = min(int(len), self.max_code_pos_len)
        code_pos = self.codes_pos[pos: pos + code_pos_len]
        code_pos = self.pad_seq(code_pos, self.max_code_pos_len)

        len, pos = self.idx_codes_pos_diff[offset]['length'], self.idx_codes_pos_diff[offset]['pos']
        code_pos_diff_len = int(len)
        code_pos_diff = self.codes_pos_diff[pos: pos + code_pos_diff_len]
        code_pos_diff = self.pad_seq(code_pos_diff, self.max_code_pos_len)

        len, pos = self.idx_codes_neg[offset]['length'], self.idx_codes_neg[offset]['pos']
        code_neg_len = min(int(len), self.max_code_neg_len)
        code_neg = self.codes_neg[pos: pos + code_neg_len]
        code_neg = self.pad_seq(code_neg, self.max_code_neg_len)

        len, pos = self.idx_codes_neg_diff[offset]['length'], self.idx_codes_neg_diff[offset]['pos']
        code_neg_diff_len = int(len)
        code_neg_diff = self.codes_neg_diff[pos: pos + code_neg_diff_len]
        code_neg_diff = self.pad_seq(code_neg_diff, self.max_code_neg_len)

        len, pos = self.idx_tests[offset]['length'], self.idx_tests[offset]['pos']
        test_len = min(int(len), self.max_test_len)
        test = self.tests[pos:pos + test_len]
        test = self.pad_seq(test, self.max_test_len)

        if self.type == 'JointEmbedder':
            test = self.pad_seq(test, max(self.max_code_pos_len, self.max_code_neg_len, self.max_test_len))
            code_pos = self.pad_seq(code_pos, max(self.max_code_pos_len, self.max_code_neg_len, self.max_test_len))
            code_pos_diff = self.pad_seq(code_pos_diff, max(self.max_code_pos_len, self.max_code_neg_len, self.max_test_len))
            code_neg = self.pad_seq(code_neg, max(self.max_code_pos_len, self.max_code_neg_len, self.max_test_len))
            code_neg_diff = self.pad_seq(code_neg_diff, max(self.max_code_pos_len, self.max_code_neg_len, self.max_test_len))

        return test, code_pos, code_neg, code_pos_diff, code_neg_diff
        
    def __len__(self):
        return self.data_len

    
def load_dict(filename):
    return json.load(open(filename, "r"))


if __name__ == '__main__':
    input_dir = './phase1_dataset_final/'
    train_set = TestOracleDatasetPhase1('JointEmbedder', input_dir, 1, 'codepos_train.h5', 723, 'codeposdiff_train.h5', 'codeneg_train.h5', 723, 'codenegdiff_train.h5', 'test_train.h5', 1625)
    train_data_loader = torch.utils.data.DataLoader(dataset=train_set, batch_size=1, shuffle=False, num_workers=1)
    vocab = load_dict(input_dir + 'vocab_phase1.json')

    k = 0
    for batch in train_data_loader:
        batch = tuple([t.numpy() for t in batch])
        test, code_pos, code_neg, code_pos_diff, code_neg_diff = batch
        k += 1
        if k > 10: break
        print('-------------------------------')
        print('====> C+: ', indexes2sent(code_pos, vocab))
        print('====> C-: ', indexes2sent(code_neg, vocab))
        print('====> Test Body: ', indexes2sent(test, vocab))
        print('====> C+ diff: ', indexes2sent(code_pos_diff, vocab))
        print('====> C- diff: ', indexes2sent(code_neg_diff, vocab))
