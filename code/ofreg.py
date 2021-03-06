import torch
import pandas as pd
import numpy as np
import utils
import models
import torch.nn as nn
import torch.optim as optim
from sklearn import metrics
from sklearn.model_selection import train_test_split
import random
import os
from torch.utils.data import TensorDataset, DataLoader
from torch import Tensor
import csv
import training

x, y, xt = utils.loaddata('OF', 1, dir="./data/", raw=True)
print('n', x,y,xt)

y = y.to_frame()
train_x = x[x.index.year==2002]
train_y = y[y.index.year==2002]

test_x = x[x.index.year == 2003]
test_x = test_x[1:]
test_y = y[y.index.year == 2003]
test_y = test_y[1:]

p = pd.read_csv("./data/train_soro.csv")
p.index = pd.DatetimeIndex(p.date)
ypreles = p.drop(p.columns.difference(['GPPp']), axis=1)[1:]


yp_train = ypreles[ypreles.index.year==2002]
print(yp_train)
yp_train = yp_train
yp_test = ypreles[ypreles.index.year==2003]
yp_test = yp_test[1:]

#print(len(x), len(y))

#print(splits)
train_x.index, train_y.index, yp_train.index = np.arange(0, len(train_x)), np.arange(0, len(train_y)), np.arange(0, len(yp_train)) 
test_x.index, test_y.index, yp_test.index = np.arange(0, len(test_x)), np.arange(0, len(test_y)), np.arange(0, len(yp_test))
print("train_x", test_y, yp_test)

print("SIZES", train_x, train_y, yp_train)

model_design = {'layersizes': [128]}

hp = {'epochs': 10000,
      'batchsize': int(128),
      'lr': 0.01,
      'eta': 0.02
      }

print(hp)
print("TRAIN_TEST", train_x.shape,  test_x.shape, "END")

data_dir = "./data/"
data = "regof"
tloss = training.finetune(hp, model_design, (train_x, train_y), (test_x, test_y), data_dir, data, reg=(yp_train, yp_test))
#pd.DataFrame.from_dict(tloss).to_csv('res2_test.csv')
print(tloss)
train_loss = tloss['train_loss']
val_loss = tloss['val_loss']

pd.DataFrame({"train_loss": train_loss, "val_loss": val_loss}).to_csv('OFreg_vloss.csv')
