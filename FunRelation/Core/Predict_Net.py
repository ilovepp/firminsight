

import os
import sys
import timeit
import numpy
import theano
import theano.tensor as T
#from Data_Process import *
from Train_LogisticRegression import *
from Train_MLP import HiddenLayer
from Train_MLP import MLP

import pickle


def prediction(proSim, proLabel,savenet = 'Core/savenet.data', batch_size = 10000):
    batch_size = len(proLabel)

    ################
    # load the net #
    ################

    f = open(savenet)

    layer1_W = pickle.load(f)
    layer1_b = pickle.load(f)

    layer2_W = pickle.load(f)
    layer2_b = pickle.load(f)

    f.close()

    #################
    # load the data #
    #################

    test_set_x = theano.shared(numpy.asarray(proSim, dtype=theano.config.floatX))
    shared_y =theano.shared(numpy.asarray(proLabel, dtype=theano.config.floatX))
    test_set_y = T.cast(shared_y, 'int32')


    n_test_batches = test_set_x.get_value(borrow=True).shape[0] // batch_size


    ##################
    # create the net #
    ##################

    #print('... building the model')

    index = T.lscalar()
    x = T.matrix('x')
    y = T.ivector('y')

    rng = numpy.random.RandomState(1234)
    predict_net = MLP(rng=rng, input=x, n_in=32, n_hidden=50, n_out=2)

    predict_net.hiddenLayer.W.set_value(layer1_W.get_value())
    predict_net.hiddenLayer.b.set_value(layer1_b.get_value())

    predict_net.logRegressionLayer.W.set_value(layer2_W.get_value())
    predict_net.logRegressionLayer.b.set_value(layer2_b.get_value())

    predict_model = theano.function(inputs=[index],
                                    outputs=[predict_net.errors(y), predict_net.logRegressionLayer.p_y_given_x],
                                    givens={x: test_set_x[index * batch_size:(index + 1) * batch_size],
                                            y: test_set_y[index * batch_size:(index + 1) * batch_size]
                                            }
                                    )
    error_now = 0
    prob = []

    for i in range(n_test_batches):
        error, result = predict_model(i)
        error_now += error
        prob.extend(result)
    error_now /=  n_test_batches

    # predict_model = theano.function(inputs = [x,y],
    #                                 outputs = [predict_net.errors(y),predict_net.logRegressionLayer.p_y_given_x]
    #                                 # givens = {x: test_set_x,
    #                                 #           y: test_set_y
    #                                 #           }
    #                                 )
    #
    # error, prob = predict_model(test_set_x,test_set_y)

    # print('the test error is %f' % error_now)

    return [item[1] for item in prob]








