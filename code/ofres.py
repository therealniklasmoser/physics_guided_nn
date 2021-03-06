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

yp_tr = pd.read_csv("./data/train_soro.csv")
yp_te = pd.read_csv("./data/train_soro.csv")
yp_tr.index = pd.DatetimeIndex(yp_tr['date'])
yp_te.index = pd.DatetimeIndex(yp_te['date'])

yptr = yp_tr.drop(yp_tr.columns.difference(['GPPp', 'ETp', 'SWp']), axis=1)
ypte = yp_te.drop(yp_te.columns.difference(['GPPp', 'ETp', 'SWp']), axis=1)

n = [1,1]
x_tr, n = utils.add_history(yptr, n, 1)
x_te, n = utils.add_history(ypte, n, 1)
x_tr = utils.standardize(x_tr)
x_te = utils.standardize(x_te)

y = y.to_frame()
train_x = x_tr[x_tr.index.year==2002]
train_y = y[y.index.year==2002]

test_x = x_te[x_te.index.year == 2003]
test_y = y[y.index.year == 2003]


#print(len(x), len(y))

#print(splits)
train_x.index, train_y.index = np.arange(0, len(train_x)), np.arange(0, len(train_y)) 
test_x.index, test_y.index = np.arange(0, len(test_x)), np.arange(0, len(test_y))
print("train_x", train_x, test_x)


model_design = {'layersizes': [256]}

hp = {'epochs': 100000,
      'batchsize': int(128),
      'lr': 0.01
      }

print(hp)
print("TRAIN_TEST", train_x.shape,  test_x.shape, "END")

data_dir = "./data/"
data = "embof"
tloss = training.finetune(hp, model_design, (train_x, train_y), (test_x, test_y), data_dir, data)
#pd.DataFrame.from_dict(tloss).to_csv('res2_test.csv')
print(tloss)
train_loss = tloss['train_loss']
val_loss = tloss['val_loss']

pd.DataFrame({"train_loss": train_loss, "val_loss": val_loss}).to_csv('OFres_vloss.csv')
