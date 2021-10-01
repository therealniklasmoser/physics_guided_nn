# !/usr/bin/env python
# coding: utf-8
import utils
import HP
import utils
import trainloaded
import embtraining
import torch
import pandas as pd
import numpy as np

x, y, xt = utils.loaddata('exp2p', 1, dir="./data/", raw=True)
x = x.drop(pd.DatetimeIndex(['2004-01-01']))
y = y.drop(pd.DatetimeIndex(['2004-01-01']))

x = x[x.index.year == 2004]
y = y[y.index.year == 2004]
y = y.to_frame()
print(x, y)
#print(len(x), len(y))
splits = 8
x.index, y.index = np.arange(0, len(x)), np.arange(0, len(y))

arch_grid = HP.ArchitectureSearchSpace(x.shape[1], y.shape[1], 800, 4)

# architecture search
layersizes, ag = HP.ArchitectureSearch(arch_grid, {'epochs': 100, 'batchsize': 8, 'lr':0.001}, x, y, splits, "EX2_arSres", exp=2, hp=True)
ag.to_csv("./EX2_resAS.csv")

#layersizes = [4, 32, 2, 16]
# Hyperparameter Search Space
hpar_grid = HP.HParSearchSpace(800)

# Hyperparameter search
hpars, grid = HP.HParSearch(layersizes, hpar_grid, x, y, splits, "EX2_hpres", exp=2, hp=True)

print( 'hyperparameters: ', hpars)


grid.to_csv("./EX2_resHP.csv")
