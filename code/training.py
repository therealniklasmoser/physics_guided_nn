# !/usr/bin/env python
# coding: utf-8
import torch
import numpy as np
import pandas as pd
import torch.nn as nn
import torch.optim as optim
from sklearn import metrics
from sklearn.model_selection import KFold
import utils
import random
import models
import os

def train(hpar, model_design, X, Y, data_dir='./'):
    # initialize data
    # hyperparameters
    n_epoch = hpar['epochs']
    batchsize = hpar['batchsize']
    lr = hpar['learningrate']
    # shuffle data
    x = random.shuffle(X.to_numpy())
    y = random.shuffle(Y.to_numpy())
    # data splits
    x_train = x[0:np.ceil(len(x)/100*80)]
    y_train = y[0:np.ceil(len(y)/100*80)]
    x_test = x[np.ceil(len(x)/100*80):]
    y_test = y[np.ceil(len(y)/100*80):]

    model = models.NMLP(model_design, X.shape[1], Y.shape[1])
    optimizer = optim.Adam(model.parameters(), lr = lr)
    criterion = nn.MSELoss()

    mae_train = []
    mae_val = []

    for epoch in range(n_epoch):

        model.train()

        nbatches = len(x_train) // batchsize
        batch_loss = []
        for n in range(nbatches):
            start, end = n * batchsize, (n + 1) * batchsize

            x = torch.tensor(x_train[start:end]).type(dtype=torch.float)
            y = torch.tensor(y_train[start:end]).type(dtype=torch.float)
            # zero parameter gradients
            optimizer.zero_grad()

            # forward
            y_hat = model(x)

            loss = criterion(y_hat, y)

            # backward
            loss.backward()
            optimizer.step()

            batch_loss.append(loss.item())
        # results per epoch
        epoch_loss = sum(batch_loss)/len(batch_loss)

        # test model
        model.eval()

        e_bl = []
        # deactivate autograd
        with torch.no_grad():
            y_hat_train = model(x_train)
            y_hat_test = model(x_test)

            val_loss = metrics.mean_absolute_error(y_test, y_hat_test)

            mae_train.append(metrics.mean_absolute_error(y_train, y_hat_train))
            mae_val.append(val_loss)

        torch.save(model.state_dict(), os.path.join(data_dir, f"{data}_model{i}.pth"))

    return {'mae_train': mae_train, 'mae_val':mae_val}







