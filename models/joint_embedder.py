import sys
sys.path.append('../')

import torch
import torch.nn as nn

from learning.modules import SequenceEncoder

class JointEmbedder(nn.Module):
    def __init__(self, config):
        super(JointEmbedder, self).__init__()
        self.config = config

        seq_max_len = config['code_len'] if config['code_len'] >= config['test_len'] else config['test_len']

        self.encoder = SequenceEncoder(config['n_words'], config['n_head'], config['n_hidden'],
                                       config['n_layers'], config['emb_size'], seq_max_len,
                                       config['dropout'])

        self.maxpooling = nn.MaxPool2d(self.config['filter_size'], self.config['stride'])

        self.fc_1 = nn.Linear(2 * (seq_max_len // config['filter_size']) * (config['emb_size'] // config['stride']), config['n_hidden'])
        self.fc_2 = nn.Linear(config['n_hidden'], config['n_hidden'])
        self.fc_3 = nn.Linear(config['n_hidden'], config['n_hidden'])
        self.fc_4 = nn.Linear(config['n_hidden'], 2)

        self.init_weights()

    def init_weights(self):
        for layer in [self.fc_1, self.fc_2, self.fc_3, self.fc_4]:
            nn.init.kaiming_uniform_(layer.weight.data, nonlinearity='relu')
            nn.init.constant_(layer.bias, 0.)

    def code_encoding(self, code):
        code_repr = self.encoder(code)
        code_repr = self.maxpooling(code_repr)
        code_repr = code_repr.view(code_repr.size(0), -1)
        return code_repr

    def test_encoding(self, test):
        test_repr = self.encoder(test)
        test_repr = self.maxpooling(test_repr)
        test_repr = test_repr.view(test_repr.size(0), -1)
        return test_repr

    def forward(self, code, test, diff, phase=1, type='simple'):
        if phase == 1:
            code_repr = self.code_encoding(code)
            test_repr = self.test_encoding(test)

            if type == 'simple':
                return torch.nn.CosineSimilarity()(code_repr, test_repr)

            elif type == 'cat':
                diff_repr = self.code_encoding(diff)
                code_diff_repr = torch.cat((code_repr, diff_repr), 1)
                test_test_repr = torch.cat((test_repr, test_repr), 1)
                return torch.nn.CosineSimilarity()(code_diff_repr, test_test_repr)        

            elif type == 'mul':
                diff_repr = self.code_encoding(diff)
                code_diff_repr = code_repr * diff_repr
                test_test_repr = test_repr * test_repr
                return torch.nn.CosineSimilarity()(code_diff_repr, test_test_repr)

        elif phase == 2:
            code_repr = self.code_encoding(code)
            test_repr = self.test_encoding(test)

            code_test_repr = torch.cat((code_repr, test_repr), dim=1)

            out = torch.relu(self.fc_1(code_test_repr))
            out = torch.relu(self.fc_2(out))
            out = torch.relu(self.fc_3(out))
            out = torch.softmax(self.fc_4(out), dim=-1)

            return out
