import os
import pandas as pd
import numpy as np
import copy
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
import torchaudio
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
import torch.nn.functional as F


class Encoder(nn.Module):
    def __init__(self, feat_dim, inp_size, hid_size):
        super().__init__()
        self.input_layer = nn.Linear(feat_dim, inp_size)
        self.layer_norm = nn.LayerNorm(feat_dim, inp_size)
        self.blstm1 = nn.LSTM(input_size=inp_size, 
                             hidden_size=hid_size, 
                             num_layers=1,
                             dropout=0.3, 
                             bidirectional=True,
                             batch_first=True)
        self.blstm2 = nn.LSTM(input_size=inp_size, 
                             hidden_size=hid_size//4, 
                             num_layers=1,
                             dropout=0.3, 
                             bidirectional=True,
                             batch_first=True)
        self.blstm3 = nn.LSTM(input_size=inp_size, 
                             hidden_size=hid_size//8, 
                             num_layers=1,
                             dropout=0.3, 
                             bidirectional=True,
                             batch_first=True)
        
    def forward(self, x, lens):
        x = self.layer_norm(x)
        x = F.leaky_relu(self.input_layer(x))
        x = self.drop(x)
        x = pack_padded_sequence(x, lens, enforce_sorted=False, batch_first=True)
        x, _ = self.blstm1(x)
        x, _ = self.blstm2(x)
        x, _ = self.blstm3(x)
        output, _ = pad_packed_sequence(x, batch_first=True)
        return output