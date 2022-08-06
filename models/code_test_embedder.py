import sys
sys.path.append('../')

import torch
import torch.nn as nn

from learning.modules import SequenceEncoder

class CodeTestEmbedder(nn.Module):
    def __init__(self, config):
        super(CodeTestEmbedder, self).__init__()
        self.config = config

        self.code_encoder = SequenceEncoder(config['code_n_words'], config['n_head'], config['n_hidden'],
                                            config['n_layers'], config['emb_size'], config['code_len'],
                                            config['dropout'])

        self.test_encoder = SequenceEncoder(config['test_n_words'], config['n_head'], config['n_hidden'],
                                            config['n_layers'], config['emb_size'], config['test_len'],
                                            config['dropout'])

        self.fc_1 = nn.Linear(((config['code_len'] // config['filter_size']) + (config['test_len'] // config['filter_size'])) * (config['emb_size'] // config['stride']), config['n_hidden'])
        self.fc_2 = nn.Linear(config['n_hidden'], config['n_hidden'])
        self.fc_3 = nn.Linear(config['n_hidden'], config['n_hidden'])
        self.fc_4 = nn.Linear(config['n_hidden'], 2)
        self.maxpooling = nn.MaxPool2d(self.config['filter_size'], self.config['stride'])
        
        self.init_weights()

    def init_weights(self):
        for layer in [self.fc_1, self.fc_2, self.fc_3, self.fc_4]:
            nn.init.kaiming_uniform_(layer.weight.data, nonlinearity='relu')
            nn.init.constant_(layer.bias, 0.)

    def code_encoding(self, code):
        code_repr = self.code_encoder(code)
        code_repr = self.maxpooling(code_repr)
        code_repr = code_repr.view(code_repr.size(0), -1)
        return code_repr

    def test_encoding(self, test):
        test_repr = self.test_encoder(test)
        test_repr = self.maxpooling(test_repr)
        test_repr = test_repr.view(test_repr.size(0), -1)
        return test_repr

    def forward(self, code, test):
        code_repr = self.code_encoding(code)
        test_repr = self.test_encoding(test)

        code_test_repr = torch.cat((code_repr, test_repr), dim=1)

        out = torch.relu(self.fc_1(code_test_repr))
        out = torch.relu(self.fc_2(out))
        out = torch.relu(self.fc_3(out))
        out = torch.softmax(self.fc_4(out), dim=-1)

        return out
