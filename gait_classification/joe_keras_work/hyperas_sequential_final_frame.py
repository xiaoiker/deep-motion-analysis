'''
    Train on t+1 vector for every t, only trying to predict the final frame, given 29 as seed.
'''

from __future__ import print_function

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, TimeDistributed
from keras.layers import LSTM
from keras.optimizers import Nadam
import keras
from hyperopt import Trials, STATUS_OK, tpe
from hyperas import optim
from hyperas.distributions import choice, uniform, conditional
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys
import theano

def data():
    '''
    Data providing function:

    This function is separated from model() so that hyperopt
    won't reload data for each evaluation run.
    '''
    data = np.load('../data/Joe/sequential_final_frame.npz')
    train_x = data['train_x']
    train_y = data['train_y']
    test_x = data['test_x']
    test_y = data['test_y']
    return train_x, train_y, test_x, test_y

def model(X_train, Y_train, X_test, Y_test):
    '''
    Model providing function:

    Create Keras model with double curly brackets dropped-in as needed.
    Return value has to be a valid python dictionary with two customary keys:
        - loss: Specify a numeric evaluation metric to be minimized
        - status: Just use STATUS_OK and see hyperopt documentation if not feasible
    The last one is optional, though recommended, namely:
        - model: specify the model just created so that we can later use it again.
    '''
    model = Sequential()
    model.add(LSTM(256, return_sequences=True, input_shape=(29, 256), consume_less='gpu', \
                    init='glorot_normal'))
    model.add(Dropout({{uniform(0, 0.5)}}))
    model.add(LSTM(512, return_sequences=True, consume_less='gpu', \
                   init='glorot_normal'))
    model.add(Dropout({{uniform(0, 0.5)}}))
    model.add(LSTM(1024, return_sequences=True, consume_less='gpu', \
                   init='glorot_normal'))
    model.add(Dropout({{uniform(0, 0.5)}}))
    model.add(TimeDistributed(Dense(256)))
    model.add(Activation(keras.layers.advanced_activations.ELU(alpha=1.0)))
    model.compile(loss='mean_squared_error', optimizer='nadam') 
    hist = model.fit(train_x, train_y, batch_size=20, nb_epoch=100, validation_data=(test_x,test_y))
    score = model.evaluate(test_x, test_y, verbose=0)

    print('Test Score:', score)

    return {'loss': score, 'status': STATUS_OK}

if __name__ == '__main__':
    best_run = optim.minimize(model=model,
                                          data=data,
                                          algo=tpe.suggest,
                                          max_evals=10,
                                          trials=Trials())
    X_train, Y_train, X_test, Y_test = data()
    print("Best Run:")
    print(best_run)
# No eval since generative model, needs all data it can get on already miniture dataset.

#TODO - replace the final 5 frames and see how it does
#TODO: - Make 2 files, time distributed and just final outputs, as well as 2 input files. Shapes are slightly different.

