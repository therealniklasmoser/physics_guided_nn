# !/usr/bin/env python
# coding: utf-8
import utils
import torch
import pandas as pd
import numpy as np
import training


x, y, xt = utils.loaddata('exp2p', 1, dir="./data/", raw=True)
print("OUUTT",x,y,xt)
# select NAS data
print(x.index)
x = x[x.index.year == 2008]
y = y[y.index.year == 2008]
x = x.drop(pd.DatetimeIndex(['2008-01-01']))
y = y.drop(pd.DatetimeIndex(['2008-01-01']))



splits = 8
print(splits)
print(x, y)
y = y.to_frame()
x.index, y.index = np.arange(0, len(x)), np.arange(0, len(y))

mlp_as = pd.read_csv("EX2_resAS.csv")
a = mlp_as.loc[mlp_as.val_loss.idxmin()][1:5]
b = a.to_numpy()
layersizes = list(b[np.isfinite(b)].astype(int))
print('layersizes', layersizes)

model_design = {'layersizes': layersizes}


mlp_hp = pd.read_csv("EX2_resHP.csv")
a = mlp_hp.loc[mlp_hp.val_loss.idxmin()][1:3]
b = a.to_numpy()
lr = b[0]
bs = b[1]
print(lr)

mlp_hp = pd.read_csv("2res_lr.csv")
a = mlp_hp.loc[mlp_hp.val_loss.idxmin()][1:3]
b = a.to_numpy()
lr = b[0]
print(lr)


hp = {'epochs': 5000,
            'batchsize': int(bs),
            'lr': lr}
print('HYPERPARAMETERS', hp)
data_dir = "./data/"
data = "2res"
#print('DATA', train_x, train_y)
#print('TX', train_x, train_y)
td, se, ae = training.train_cv(hp, model_design, x, y, data_dir, splits, data, reg=None, emb=False, exp=2)
print(td, se, ae)
pd.DataFrame.from_dict(td).to_csv('2res_eval_tloss.csv')
pd.DataFrame.from_dict(se).to_csv('2res_eval_vseloss.csv')
pd.DataFrame.from_dict(ae).to_csv('2res_eval_vaeloss.csv')