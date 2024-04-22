import glob, contextlib, os
import pandas as pd
import numpy as np
from multiprocessing import Manager
from functools import partial

from config import methods

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, LabelBinarizer
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import RepeatedKFold, cross_val_score, KFold, cross_val_predict
from sklearn.feature_selection import VarianceThreshold
from sklearn.svm import SVR, SVC
import xgboost as xgb

import argparse

parser = argparse.ArgumentParser(prog='Optimized model rebuilder', 
                                description='Rebuilds the model from the optimized trial parameters,\nsaving it as an UNTRAINED pipeline in pickle')
parser.add_argument('-d', '--descdir', required=True, 
    help='the folder containing descriptor files. Can contain folders separated by descriptor type')
parser.add_argument('-m', '--modeldir', required=True, 
    help='the folder containing model output files. Should contain "trials.all" file.')
parser.add_argument('-n', '--number', type=int, required=True, 
    help='the trial number for the model to be rebuilt.')
parser.add_argument('-o', '--outdir', required=True, 
    help='the output folder for the models.')


if __name__ == '__main__':
    args = parser.parse_args()
    descdir = args.descdir
    modeldir = args.modeldir
    number = args.number
    outdir = args.outdir

    if os.path.exists(outdir):
        print('The output directory {} already exists. The data may be overwritten'.format(outdir))
    else:
        os.makedirs(outdir)
        print('The output directory {} created'.format(outdir))

    trials = pd.read_table(os.path.join(modeldir, 'trials.all'), sep=' ')
    rebuild_trial = trials.iloc[number]

    pipeline_steps = []

    desc_name = rebuild_trial['desc']
    if os.path.isdir(os.path.join(descdir, desc_name.split('-')[0])):
        desc_file = os.path.join(descdir, desc_name.split('-')[0], desc_name+'.pkl')
    else:
        desc_file = os.path.join(descdir, desc_name+'.pkl')
    with open(desc_file, 'rb') as f:
        desc_calculator = pickle.load(f)
    pipeline_steps.append(('descriptor_calculator', desc_calculator))

    if rebuild_trial['scaling'] == 'scaled':
        pipeline_steps.append(('scaler', MinMaxScaler()))

    pipeline_steps.append(('variance', VarianceThreshold()))

    params = line[rebuild_trial.index[list(rebuild_trial.index).index('method')+1:]].to_dict()
    model = eval(methods[method])
    pipeline_steps.append(('model', model()))

    pipeline = Pipeline(pipeline_steps)

    modelfile_name = '_'.join([rebuild_trial['method'], 'trial'+str(number), desc_name])
    with open(os.path.join(outdir, modelfile_name+'.pkl')) as f:
        pickle.dump(pipeline, f)

