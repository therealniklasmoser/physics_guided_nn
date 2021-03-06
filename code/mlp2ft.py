# !/usr/bin/env python
# coding: utf-8
import utils
import HP
import torch
import pandas as pd
import numpy as np
import random
import training


x, y, xt, yp = utils.loaddata('exp2', 1, dir="./data/", raw=True)

# select NAS data
print(x.index)

x = x[x.index.year == 2004]
y = y[y.index.year == 2004]

x = x.drop(pd.DatetimeIndex(['2004-01-01']))
y = y.drop(pd.DatetimeIndex(['2004-01-01']))
print(x,y)
splits = 8

x.index = np.arange(0, len(x))
y.index = np.arange(0, len(y))

train_idx = np.arange(0, np.ceil(len(x)/splits)*7)
test_idx = np.arange(np.ceil(len(x)/splits)*7, len(x))

train_x, train_y = x[x.index.isin(train_idx)], y[y.index.isin(train_idx)]
test_x, test_y = x[x.index.isin(test_idx)], y[y.index.isin(test_idx)]

print("TRAINTEST",train_x, test_x)

res_as = pd.read_csv("EX2_mlpAS.csv")
a = res_as.loc[res_as.val_loss.idxmin()][1:5]
b = a.to_numpy()
layersizes = list(b[np.isfinite(b)].astype(int))
print('layersizes', layersizes)

model_design = {'layersizes': layersizes}

res_hp = pd.read_csv("EX2_mlpHP.csv")
a = res_hp.loc[res_hp.val_loss.idxmin()][1:3]
b = a.to_numpy()
lrini = b[0]
bs = b[1]

lrs = []
for i in range(300):
    l = round(random.uniform(1e-8, lrini),8)
    if l not in lrs:
        lrs.append(l)

print(lrs, len(lrs))
mse_train = []
mse_val = []
print("trainshape",train_x.shape, train_y.to_frame().shape)

for i in range(len(lrs)):

    hp = {'epochs': 2000,
          'batchsize': int(bs),
          'lr': lrs[i]}
    
    data_dir = "./data/"
    data = "2mlp"
    loss = training.finetune(hp, model_design, (train_x, train_y.to_frame()), (test_x, test_y.to_frame()), data_dir, data, reg=None, emb=False)
    mse_train.append(np.mean(loss['train_loss']))
    mse_val.append(np.mean(loss['val_loss']))

df = pd.DataFrame(lrs)
df['train_loss'] = mse_train
df['val_loss'] = mse_val
print("Random hparams search best result:")
print(df.loc[[df["val_loss"].idxmin()]])
lr = lrs[df["val_loss"].idxmin()]
print("Dataframe:", df)

df.to_csv("2mlp_lr.csv")
