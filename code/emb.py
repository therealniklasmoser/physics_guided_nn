# !/usr/bin/env python
# coding: utf-8
import utils
import HP
import utils
import trainloaded
import torch
import pandas as pd
import numpy as np

x, y, mn, std, xt = utils.loaddata('NAS', 0, dir="./data/", raw=True)
xt = xt.drop(['date', 'GPP', 'ET'], axis=1)

yp_tr = pd.read_csv("./data/train_soro.csv")
yp_te = pd.read_csv("./data/test_soro.csv")
yp_tr.index = pd.DatetimeIndex(yp_tr['date'])
yp_te.index = pd.DatetimeIndex(yp_te['date'])
yptr = yp_tr.drop(yp_tr.columns.difference(['GPPp']), axis=1)
ypte = yp_te.drop(yp_te.columns.difference(['GPPp']), axis=1)

yp = pd.concat([yptr, ypte])


ypp = (yp-mn['GPP'])/std['GPP']


splits = len(x.index.year.unique())

x.index, y.index, ypp.index = np.arange(0, len(x)), np.arange(0, len(y)), np.arange(0, len(ypp))

arch_grid = HP.ArchitectureSearchSpace(x.shape[1], y.shape[1], 150, 4, emb=True)

# architecture search
layersizes, ag = HP.ArchitectureSearch(arch_grid, {'epochs': 20, 'batchsize': 16, 'lr':0.01, 'eta': 0.2}, x, y, splits, "arSemb", reg=ypp, emb=True, raw= xt, mn=mn, std=std)

ag.to_csv("./NembAS2.csv")

#layersizes = [[16], [32]]
# Hyperparameter Search Space
hpar_grid = HP.HParSearchSpace(50, reg=True, emb=True)

# Hyperparameter search
hpars, grid = HP.HParSearch(layersizes, hpar_grid, x, y, splits, "hpemb", reg=ypp, emb=True, raw=xt, mn=mn, std=std)

print( 'hyperparameters: ', hpars)


grid.to_csv("./NembHP2.csv")

