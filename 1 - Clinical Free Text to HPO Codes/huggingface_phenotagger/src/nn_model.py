# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 09:04:13 2020

@author: luol2
"""

import time
import sys
import numpy as np
import keras
from src.nn_represent import CNN_RepresentationLayer,BERT_RepresentationLayer
from keras.layers import *
from keras.models import Model
from keras_bert import load_trained_model_from_checkpoint




class bioTag_CNN():
    def __init__(self, model_files):
        self.model_type='cnn'
        model_test_type='cnn'
        self.fea_dict = {'word': 1,
                         'char': 1,
                         'lemma':0,
                         'pos':0}
    
        self.hyper = {'sen_max'      :20,
                      'word_max'     :40,
                      'charvec_size' :50,
                      'pos_size'     :50}
             
        self.w2vfile=model_files['w2vfile']      
        self.charfile=model_files['charfile']
        self.labelfile=model_files['labelfile']
        self.posfile=model_files['posfile']

        vocab={'char':self.charfile,'label':self.labelfile,'pos':self.posfile}
        print('loading w2v model.....') 
        self.rep = CNN_RepresentationLayer(self.w2vfile,vocab_file=vocab, frequency=400000)
         
        print('building  model......')
        all_fea = []
        fea_list = []
        
        if self.fea_dict['word'] == 1:
            word_input = Input(shape=(self.hyper['sen_max'],), dtype='int32', name='word_input')  
            all_fea.append(word_input)
            word_fea = Embedding(self.rep.vec_table.shape[0], self.rep.vec_table.shape[1], weights=[self.rep.vec_table], trainable=True,mask_zero=False, input_length=self.hyper['sen_max'], name='word_emd')(word_input)
            fea_list.append(word_fea)
    
        if self.fea_dict['char'] == 1:
            char_input = Input(shape=(self.hyper['sen_max'],self.hyper['word_max']), dtype='int32', name='char_input')
            all_fea.append(char_input)
            char_fea = TimeDistributed(Embedding(self.rep.char_table_size, self.hyper['charvec_size'], trainable=True,mask_zero=False),  name='char_emd')(char_input)
            char_fea = TimeDistributed(Conv1D(self.hyper['charvec_size']*2, 3, padding='same',activation='relu'), name="char_cnn")(char_fea)
            char_fea_max = TimeDistributed(GlobalMaxPooling1D(), name="char_pooling_max")(char_fea)
            fea_list.append(char_fea_max)
            
        if self.fea_dict['lemma'] == 1:
            lemma_input = Input(shape=(self.hyper['sen_max'],), dtype='int32', name='lemma_input')  
            all_fea.append(lemma_input)
            lemma_fea = Embedding(self.rep.vec_table.shape[0], self.rep.vec_table.shape[1], weights=[self.rep.vec_table], trainable=True,mask_zero=False, input_length=self.hyper['sen_max'], name='lemma_emd')(lemma_input)
            fea_list.append(lemma_fea)
            
        if self.fea_dict['pos'] == 1:
            pos_input = Input(shape=(self.hyper['sen_max'],), dtype='int32', name='pos_input')
            all_fea.append(pos_input)
            pos_fea = Embedding(self.rep.pos_table_size, self.hyper['pos_size'], trainable=True,mask_zero=False, input_length=self.hyper['sen_max'], name='pos_emd')(pos_input)
            fea_list.append(pos_fea)    
    
        if len(fea_list) == 1:
            concate_vec = fea_list[0]
        else:
            concate_vec = Concatenate()(fea_list)
    
        concate_vec = Dropout(0.4)(concate_vec)
    
        # model
        if model_test_type=='cnn':    
            cnn = Conv1D(1024, 1, padding='valid', activation='relu',name='cnn1')(concate_vec)
            cnn = GlobalMaxPooling1D()(cnn)
        elif model_test_type=='lstm':
            bilstm = Bidirectional(LSTM(200, return_sequences=True, implementation=2, dropout=0.4, recurrent_dropout=0.4), name='bilstm1')(concate_vec)
            cnn = GlobalMaxPooling1D()(bilstm)

    
        dense = Dense(1024, activation='relu')(cnn)
        dense= Dropout(0.4)(dense)
        output = Dense(self.rep.label_table_size, activation='softmax')(dense)
        self.model = Model(inputs=all_fea, outputs=output)
    def load_model(self,model_file):
        self.model.load_weights(model_file)
        #self.model.summary()        
        print('load cnn model done!')

class bioTag_BERT():
    def __init__(self, model_files):
        self.model_type='bert'
        self.maxlen = 64
        config_path = model_files['config_path']
        checkpoint_path = model_files['checkpoint_path']
        vocab_path = model_files['vocab_path']
        self.label_file=model_files['labelfile']
    
        self.rep = BERT_RepresentationLayer( vocab_path, self.label_file)
        
        
        bert_model = load_trained_model_from_checkpoint(config_path, checkpoint_path, training=False, trainable=True,seq_len=self.maxlen)
    
        x1_in = Input(shape=(None,))
        x2_in = Input(shape=(None,))
        x = bert_model([x1_in, x2_in])
        x = Lambda(lambda x: x[:, 0])(x)
        outputs = Dense(self.rep.label_table_size, activation='softmax')(x)
    
        self.model = Model(inputs=[x1_in,x2_in], outputs=outputs)

    def load_model(self,model_file):
        self.model.load_weights(model_file)
        #self.model.summary()        

class bioTag_Bioformer():
    def __init__(self, model_files):
        self.model_type='bioformer'
        self.maxlen = 32
        config_path = model_files['config_path']
        checkpoint_path = model_files['checkpoint_path']
        vocab_path = model_files['vocab_path']
        self.label_file=model_files['labelfile']
    
        self.rep = BERT_RepresentationLayer( vocab_path, self.label_file)
        
        
        bert_model = load_trained_model_from_checkpoint(config_path, checkpoint_path, training=False, trainable=True,seq_len=self.maxlen)
    
        x1_in = Input(shape=(None,))
        x2_in = Input(shape=(None,))
        x = bert_model([x1_in, x2_in])
        x = Lambda(lambda x: x[:, 0])(x)
        outputs = Dense(self.rep.label_table_size, activation='softmax')(x)
    
        self.model = Model(inputs=[x1_in,x2_in], outputs=outputs)

    def load_model(self,model_file):
        self.model.load_weights(model_file)
        #self.model.summary()
        print('load bioformer model done!')
      
