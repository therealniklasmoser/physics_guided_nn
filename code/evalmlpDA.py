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
import argparse

parser = argparse.ArgumentParser(description='Define data usage and splits')
#parser.add_argument('-d', metavar='data', type=str, help='define data usage: full vs sparse')
#parser.add_argument('-a', metavar='da', type=int, help='define type of domain adaptation')
#parser.add_argument('-s', metavar='splits', type=int, help='number of splits for CV')
#args = parser.parse_args()

#print(args)

def evalmlpDA(data_use="full", da=1, of=True):
    '''
    da specifies Domain Adaptation:                                                                                                                                       da = 1: using pretrained weight and fully retrain network                                                                                                 
        da = 2: retrain only last layer.
    '''

    if data_use == 'sparse':
        # Load hyytiala
        x, y, xt = utils.loaddata('validation', 1, dir="./data/", raw=True, sparse=True)
    else:
        x, y, xt = utils.loaddata('validation', 1, dir="./data/", raw=True)

    y = y.to_frame()


    train_x = x[~x.index.year.isin([2004, 2005, 2007,2008])][1:]
    train_y = y[~y.index.year.isin([2004, 2005, 2007,2008])][1:]

    splits = len(train_x.index.year.unique())
    test_x = x[x.index.year == 2008]
    test_y = y[y.index.year == 2008]
    print('CHECK DATA', train_x, train_y, test_x, test_y)
    train_x.index, train_y.index = np.arange(0, len(train_x)), np.arange(0, len(train_y)) 
    test_x.index, test_y.index = np.arange(0, len(test_x)), np.arange(0, len(test_y))
    
    # Architecture
    res_as = pd.read_csv(f"./results/NmlpAS_{data_use}.csv")
    a = res_as.loc[res_as.ind_mini.idxmin()][1:5]
    b = a.to_numpy()
    layersizes = list(b[np.isfinite(b)].astype(int))
    print('layersizes', layersizes)

    model_design = {'layersizes': layersizes}

    # Hyperparameters
    res_hp = pd.read_csv(f"./results/NmlpHP_{data_use}.csv")
    a = res_hp.loc[res_hp.ind_mini.idxmin()][1:3]
    b = a.to_numpy()
    lr = b[0]
    bs = b[1]
    print('Batch Size and LR', b)
    # Learningrate
    if of:
        res_hp = pd.read_csv(f"./results/mlp_lr_{data_use}.csv")
        a = res_hp.loc[res_hp.ind_mini.idxmin()][1:3]
        b = a.to_numpy()
        lr = b[0]
    
    # originally 5000 epochs
    hp = {'epochs': 5000,
          'batchsize': int(bs),
          'lr': lr}
    print('HYPERPARAMETERS', hp)
    data_dir = "./data/"
    data = f"mlpDA_pretrained_{data_use}"
    
    tloss = training.train_cv(hp, model_design, train_x, train_y, data_dir, splits, data, domain_adaptation=da, reg=None, emb=False, hp=False)
    print(tloss)
    train_loss = tloss['train_loss']
    val_loss = tloss['val_loss']
    t1 = []
    t2 = []
    t3 = []
    t4 = []
    #t5 = []
    #t6 = []
    #originally use 5000 epochs!
    for i in range(hp['epochs']):
        t1.append(train_loss[0][i])
        t2.append(train_loss[1][i])
        t3.append(train_loss[2][i])
        t4.append(train_loss[3][i])
     #   t5.append(train_loss[4][i])
     #   t6.append(train_loss[5][i])
    v1 = []
    v2 = []
    v3 = []
    v4 = []
    # v5 = []
    # v6 = []
    for i in range(hp['epochs']):
        v1.append(val_loss[0][i])
        v2.append(val_loss[1][i])
        v3.append(val_loss[2][i])
        v4.append(val_loss[3][i])
      #  v5.append(val_loss[4][i])
      #  v6.append(val_loss[5][i])

    pd.DataFrame({"f1": v1, "f2": v2, "f3":v3, "f4": v4}).to_csv(f'./results/mlpDA{da}_vloss_{data_use}.csv')
    #tloss = training.train(hp, model_design, train_x, train_y, data_dir, None, data, reg=None, emb=False)
    #tloss = cv.train(hp, model_design, train_x, train_y, data_dir=data_dir, data=data, splits=splits)
    #print("LOSS", tloss)
    pd.DataFrame({"f1": t1, "f2": t2, "f3":t3, "f4": t4}).to_csv(f'./results/mlpDA{da}_trainloss_{data_use}.csv')
    
    # Evaluation
    mse = nn.MSELoss()
    mae = nn.L1Loss()
    x_train, y_train = torch.tensor(train_x.to_numpy(), dtype=torch.float32), torch.tensor(train_y.to_numpy(), dtype=torch.float32)
    x_test, y_test = torch.tensor(test_x.to_numpy(), dtype=torch.float32), torch.tensor(test_y.to_numpy(), dtype=torch.float32)
    
    train_rmse = []
    train_mae = []
    test_rmse = []
    test_mae = []
    
    preds_train = {}
    preds_test = {}
    
    for i in range(splits):
        i += 1
        #import model
        model = models.NMLP(x.shape[1], y.shape[1], model_design['layersizes'])
        if data_use == 'sparse':
            model.load_state_dict(torch.load(''.join((data_dir, f"mlpDA{da}_model{i}.pth"))))
        else:
            model.load_state_dict(torch.load(''.join((data_dir, f"mlpDA{da}_model{i}.pth"))))
        model.eval()
        with torch.no_grad():
            p_train = model(x_train)
            p_test = model(x_test)
            preds_train.update({f'train_mlp{i}': p_train.flatten().numpy()})
            preds_test.update({f'test_mlp{i}': p_test.flatten().numpy()})
            train_rmse.append(mse(p_train, y_train).tolist())
            train_mae.append(mae(p_train, y_train).tolist())
            test_rmse.append(mse(p_test, y_test).tolist())
            test_mae.append(mae(p_test, y_test).tolist())

        performance = {'train_RMSE': train_rmse,
                       'train_MAE': train_mae,
                       'test_RMSE': test_rmse,
                       'test_mae': test_mae}
        
        print(preds_train)

    pd.DataFrame.from_dict(performance).to_csv(f'./results/mlpDA{da}_eval_performance_{data_use}.csv')
    pd.DataFrame.from_dict(preds_train).to_csv(f'./results/mlpDA{da}_eval_preds_train_{data_use}.csv')
    pd.DataFrame.from_dict(preds_test).to_csv(f'./results/mlpDA{da}_eval_preds_test_{data_use}.csv')



if __name__ == '__main__':
   evalmlpDA(data_use="full", da=1)
   evalmlpDA(data_use="sparse", da=1)
   evalmlpDA(data_use="full", da=2)
   evalmlpDA(data_use="sparse", da=2)
   evalmlpDA(data_use="full", da=3)
   evalmlpDA(data_use="sparse", da=3)

'''
with open('mlp_eval_performance.csv', 'w') as f:  # You will need 'wb' mode in Python 2.x
    w = csv.DictWriter(f, performance.keys())
    w.writeheader()
    w.writerow(performance)


with open('mlp_eval_preds.csv', 'w') as f:  # You will need 'wb' mode in Python 2.x
    w = csv.DictWriter(f, preds.keys())
    w.writeheader()
    w.writerow(preds)
'''
    



    















