# !/usr/bin/env python
# coding: utf-8
import utils
import HP
import torch
import pandas as pd
import numpy as np
import random
import training

x, y, xt, yp = utils.loaddata('exp2', 0, dir="./data/", raw=True)

swmn = np.mean(yp.SWp)
swstd = np.std(yp.SWp)
xt = xt.drop(['date', 'ET', 'GPP', 'X', 'Unnamed: 0', 'GPPp', 'ETp', 'SWp'], axis = 1)
yp = yp.drop(yp.columns.difference(['GPPp']), axis=1)

yp = yp[yp.index.year == 2004]
x = x[x.index.year == 2004]
y = y[y.index.year == 2004]
y = y.to_frame()
print(x, y, yp)
splits = 8
x.index, y.index, yp.index, xt.index = np.arange(0, len(x)), np.arange(0, len(y)), np.arange(0, len(yp)), np.arange(0, len(xt))

#x.index = np.arange(0, len(x))
#y.index = np.arange(0, len(y))

train_idx = np.arange(0, np.ceil(len(x)/splits)*7)
test_idx = np.arange(np.ceil(len(x)/splits)*7, len(x))

train_x, train_y, train_yp, train_xr = x[x.index.isin(train_idx)], y[y.index.isin(train_idx)], yp[yp.index.isin(train_idx)], xt[xt.index.isin(train_idx)]
test_x, test_y, test_yp, test_xr = x[x.index.isin(test_idx)], y[y.index.isin(test_idx)], yp[yp.index.isin(test_idx)], xt[xt.index.isin(test_idx)]

print("TRAINTEST",train_x, test_x)


res_as = pd.read_csv("Nemb2AS.csv")
a = res_as.loc[res_as.val_loss.idxmin()][1:2]
b = str(a.values).split("[")[-1].split("]")[0].split(",")
c = [int(bb) for bb in b]
a = res_as.loc[res_as.val_loss.idxmin()][2:3]
b = str(a.values).split("[")[-1].split("]")[0].split(",")
d = [int(bb) for bb in b]
layersizes = [c, d]
print('layersizes', layersizes)

model_design = {'layersizes': layersizes}

res_hp = pd.read_csv("Nemb2HP_m300.csv")
a = res_hp.loc[res_hp.val_loss.idxmin()][1:4]
b = a.to_numpy()
lrini = b[0]
bs = b[1]
eta = b[2]

lrs = []
for i in range(100):
    l = round(random.uniform(1e-8, lrini),8)
    if l not in lrs:
        lrs.append(l)

print(lrs, len(lrs))
mse_train = []
mse_val = []

for i in range(100):

    hp = {'epochs': 500,
          'batchsize': int(bs),
          'lr': lrs[i],
          'eta': eta}
    
    data_dir = "./data/"
    data = "emb2"
    loss = training.finetune(hp, model_design, (train_x, train_y), (test_x, test_y), data_dir, data, reg=(train_yp, test_yp), raw=(train_xr, test_xr) , emb=True, sw= (swmn, swstd), embtp=2, exp=2)
    mse_train.append(np.mean(loss['train_loss']))
    mse_val.append(np.mean(loss['val_loss']))

df = pd.DataFrame(lrs)
df['train_loss'] = mse_train
df['val_loss'] = mse_val
print("Random hparams search best result:")
print(df.loc[[df["val_loss"].idxmin()]])
lr = lrs[df["val_loss"].idxmin()]
print("Dataframe:", df)

df.to_csv("EX2_300emb2_lr.csv")
