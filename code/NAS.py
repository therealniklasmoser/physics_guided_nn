# !/usr/bin/env python
# coding: utf-8
import torch
import pandas as pd
import numpy as np
import random

def ArchitectureSearchSpace(input_size, output_size, grid_size, max_layers):
    grid = []
    for i in range(grid_size):
        layer_size = [input_size]
        nlayers = random.randint(1, max_layers)
        for i in range(nlayers):
            size = random.choice([2, 4, 8, 16, 32, 64, 128])
            layer_size.append(size)
        layer_size.append(output_size)
        if layer_size not in grid:
            grid.append(layer_size)
        return grid

def ArchitectureSearch(grid, parameters):
    mae_train = []
    mae_val = []

    for i in range(len(grid)):
        model_design = {"layer_sizes":grid[i]}
        running_losses = 1# train model
        mae_train.append(np.mean(np.transpose(running_losses["mae_train"])[-1]))
        mae_val.append(np.mean(np.transpose(running_losses["mae_val"])[-1]))
        print(f"fitted model {i}")

    df = pd.DataFrame(grid)
    df["mae_train"] = mae_train
    df["mae_val"] = mae_val
    print("Random architecture search best result:")
    print(df.loc[[df["mae_val"].idxmin()]])
    layersizes = grid[df["mae_val"].idxmin()]

    return layersizes


def HParSearchSpace(gridsize):
    grid = []
    for i in range(gridsize):
        learning_rate = random.choice([0.01, 0.05, 0.001, 0.005])
        batchsize = random.choice([4, 8, 16, 32, 64, 128])
        if [learning_rate, batchsize] not in grid:
            grid.append([learning_rate, batchsize])
    return grid



def HParSearch(layersizes):
    grid = HParSearchSpace(40)

    model_design = {"layer_sizes": layersizes}
    mae_train = []
    mae_val = []

    for i in range(len(grid)):
        hparams = {"epochs": 300,
                   "batchsize": grid[i][1],
                   "learningrate": grid[i][0],
                   "history": 1}

        running_losses = training.train(hparams, model_design, X_P1.to_numpy(), Y_P1.to_numpy(), "randomsearch")
        mae_train.append(np.mean(np.transpose(running_losses["mae_train"])[-1]))
        mae_val.append(np.mean(np.transpose(running_losses["mae_val"])[-1]))
        print(f"fitted model {i}")

    df = pd.DataFrame(grid)
    df["mae_train"] = mae_train
    df["mae_val"] = mae_val
    print("Random hparams search best result:")
    print(df.loc[[df["mae_val"].idxmin()]])
    hparams = grid[df["mae_val"].idxmin()]

    return hparams