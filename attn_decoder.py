from data import preproc_text, Data, collate_custom
from encoder import Encoder

import os
import numpy as np
import torch.utils.data as data
import torch
import torch.nn as nn
from torch.distributions.gumbel import Gumbel




class Attention(nn.Module):
    def __init__(self):
        super(Attention, self).__init__()
    def forward(self, query, key, value, lens):
        '''
        :param query :(N,context_size) Query is the output of LSTMCell from Decoder
        :param key: (T,N,key_size) Key Projection from Encoder per time step
        :param value: (T,N,value_size) Value Projection from Encoder per time step
        :return output: Attended Context
        :return attention_mask: Attention mask that can be plotted  
        '''
        key=torch.transpose(key, 0, 1)
        attention=torch.bmm(key, query.unsqueeze(2)).squeeze(2)
        mask=torch.arange(attention.size(1)).unsqueeze(0) >= lens.unsqueeze(1)
        mask=mask.to(device)
        attention.masked_fill_(mask, -1e9)
        attention=nn.functional.softmax(attention, dim=1)
        value=torch.transpose(value,0,1)
        context=torch.bmm(attention.unsqueeze(1), value).squeeze(1)
        return context, attention



class Decoder(nn.Module):
    def __init__(self, alphabet_size, hidden_dim, value_size=128, key_size=128,  isAttended=True):
        super(Decoder, self).__init__()
        self.embedding = nn.Embedding(alphabet_size, hidden_dim, padding_idx=0)

        self.lstm1 = nn.LSTMCell(input_size=hidden_dim+value_size, hidden_size=hidden_dim)
        self.lstm2 = nn.LSTMCell(input_size=hidden_dim, hidden_size=key_size)
        self.isAttended = isAttended
        if(isAttended):
            self.attention = Attention()
        self.mos = nn.Linear(key_size+value_size,alphabet_size)

    def forward(self, key, values, lens, text, device, train=True):
        '''
        :param key :(T,N,key_size) Output of the Encoder Key projection layer
        :param values: (T,N,value_size) Output of the Encoder Value projection layer
        :param text: (N,text_len) Batch input of text with text_length
        :param train: Train or eval mode
        :return predictions: Returns the character perdiction probability 
        '''
        batch_size=key.shape[1]
        if(train):
            text=torch.transpose(text,0,1)
            max_len=text.shape[1]
            embeddings=self.embedding(text)
        else:
            max_len = 200
        
        predictions = []

        hidden_states = [None, None]
        prediction = torch.zeros(batch_size, 1).to(device)
        context=values[0,:,:]
        for i in range(max_len):
            if(train):
                if np.random.random_sample() > 0.6:
                    prediction = Gumbel(prediction.to('cpu'), torch.tensor([0.4])).sample().to(device)
                    embed = self.embedding(prediction.argmax(dim=-1))
                    print("embed1", embed.shape)
                else:
                    embed = embeddings[:,i,:]
                    print("embed2:", embed.shape)
            else:
                embed = self.embedding(prediction.argmax(dim=-1))   
                print("embed2:", embed.shape)

            print(embed.shape, context.shape) 
            inp = torch.cat([embed,context], dim=1)
            hidden_states[0] = self.lstm1(inp,hidden_states[0])
            
            inp_2 = hidden_states[0][0]
            hidden_states[1] = self.lstm2(inp_2,hidden_states[1])

            output = hidden_states[1][0]
            context, attention=self.attention(output, key, values, lens)
            prediction = self.mos(torch.cat([output, context], dim=1))
            predictions.append(prediction.unsqueeze(1))

            return torch.cat(predictions, dim=1)





corpus_path = '/nobackup/anakuzne/data/cv/cv-corpus-6.1-2020-12-11/eu'
char2ind = preproc_text(corpus_path, 'eu')

dataset_train = Data(os.path.join(corpus_path, 'train.tsv'), os.path.join(corpus_path, 'clips'), char2ind)
loader_train = data.DataLoader(dataset_train, batch_size=5, 
                               shuffle=True, collate_fn=collate_custom)

device ="cuda:1"

encoder = Encoder(120, 256)
decoder = Decoder(len(char2ind), 512)
encoder.to(device)
decoder.to(device)

for batch in loader_train:
    x = batch["feat"].to(device)
    xlens = batch['alens']
    y = batch['trans'].to(device)
    print("text", y.shape)
    keys, values = encoder(x, xlens)
    out = decoder(keys, values, xlens, y, device)
    print("dec out:", out.shape)