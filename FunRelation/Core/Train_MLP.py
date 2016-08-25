__author__ = 'changqing'
__docformat__ = 'restructedtext en'

import os
import sys
import timeit
import numpy
import theano
import theano.tensor as T
import six.moves.cPickle as pickle
from Train_LogisticRegression import *


class HiddenLayer(object):
    def __init__(self, rng, input, n_in, n_out, W=None, b=None, activation=T.tanh):
        self.input = input
        if W is None:
            W_values = numpy.asarray(rng.uniform(low=-numpy.sqrt(6. / (n_in + n_out)), high=numpy.sqrt(6. / (n_in + n_out)), size=(n_in, n_out)),dtype=theano.config.floatX)

            W = theano.shared(value=W_values, name='W', borrow=True)
        if b is None:
            b_values = numpy.zeros((n_out,), dtype=theano.config.floatX)
            b = theano.shared(value=b_values, name='b', borrow=True)
        self.W = W
        self.b = b
        lin_output = T.dot(input, self.W) + self.b
        self.output = (lin_output if activation is None else activation(lin_output))
        self.params = [self.W, self.b]


class MLP(object):
    def __init__(self, rng, input, n_in, n_hidden, n_out):
        self.hiddenLayer = HiddenLayer(rng=rng, input=input, n_in=n_in, n_out=n_hidden, activation=T.tanh)
        self.logRegressionLayer = LogisticRegression(input=self.hiddenLayer.output, n_in=n_hidden, n_out=n_out)
        self.L1 = (abs(self.hiddenLayer.W).sum() + abs(self.logRegressionLayer.W).sum())
        self.L2_sqr = ((self.hiddenLayer.W ** 2).sum() + (self.logRegressionLayer.W ** 2).sum())
        self.negative_log_likelihood = (self.logRegressionLayer.negative_log_likelihood)
        self.errors = self.logRegressionLayer.errors
        self.params = self.hiddenLayer.params + self.logRegressionLayer.params
        self.input = input


def test_mlp(datasets,learning_rate=0.01, L1_reg=0.00, L2_reg=0.0001, n_epochs=1000, batch_size=20, n_hidden=50):

    train_set_x, train_set_y = datasets[0]
    valid_set_x, valid_set_y = datasets[1]
    test_set_x, test_set_y = datasets[2]

    # compute number of minibatches for training, validation and testing
    n_train_batches = train_set_x.get_value(borrow=True).shape[0] // batch_size
    n_valid_batches = valid_set_x.get_value(borrow=True).shape[0] // batch_size
    n_test_batches = test_set_x.get_value(borrow=True).shape[0] // batch_size

    print n_train_batches,n_valid_batches,n_test_batches

    ######################
    # BUILD ACTUAL MODEL #
    ######################
    print('...building the model')
    index = T.lscalar()
    x = T.matrix('x')
    y = T.ivector('y')
    rng = numpy.random.RandomState(1234)
    classifier = MLP(rng=rng, input=x, n_in=31, n_hidden=n_hidden, n_out=2)
    cost = (classifier.negative_log_likelihood(y) + L1_reg * classifier.L1 + L2_reg * classifier.L2_sqr)
    test_model = theano.function(inputs=[index], outputs=classifier.errors(y), givens={x: test_set_x[index * batch_size:(index + 1) * batch_size], y: test_set_y[index * batch_size:(index + 1) * batch_size]})
    validate_model = theano.function(inputs=[index], outputs=classifier.errors(y), givens={x: valid_set_x[index * batch_size:(index + 1) * batch_size], y: valid_set_y[index * batch_size:(index + 1) * batch_size]})
    gparams = [T.grad(cost, param) for param in classifier.params]
    updates = [(param, param - learning_rate * gparam) for param, gparam in zip(classifier.params, gparams)]
    train_model = theano.function(inputs=[index], outputs=cost, updates=updates, givens={x: train_set_x[index * batch_size: (index + 1) * batch_size], y: train_set_y[index * batch_size: (index + 1) * batch_size]})

    ###############
    # TRAIN MODEL #
    ###############
    print('... training')

    # early-stopping parameters
    patience = 10000
    patience_increase = 2
    improvement_threshold = 0.995
    validation_frequency = min(n_train_batches, patience // 2)

    best_validation_loss = numpy.inf
    best_iter = 0
    test_score = 0.
    start_time = timeit.default_timer()

    epoch = 0
    done_looping = False

    while (epoch < n_epochs) and (not done_looping):
        epoch = epoch + 1
        for minibatch_index in range(n_train_batches):


            minibatch_avg_cost = train_model(minibatch_index)
            # iteration number
            iter = (epoch - 1) * n_train_batches + minibatch_index

            if (iter + 1) % validation_frequency == 0:
                # compute zero-one loss on validation set
                validation_losses = [validate_model(i) for i in range(n_valid_batches)]
                this_validation_loss = numpy.mean(validation_losses)
                print(
                    'epoch %i, minibatch %i/%i, validation error %f %%' %
                    (
                        epoch,
                        minibatch_index + 1,
                        n_train_batches,
                        this_validation_loss * 100.
                    )
                )

                # if we got the best validation score until now
                if this_validation_loss < best_validation_loss:
                    #improve patience if loss improvement is good enough
                    if (
                        this_validation_loss < best_validation_loss *
                        improvement_threshold
                    ):
                        patience = max(patience, iter * patience_increase)

                    best_validation_loss = this_validation_loss
                    best_iter = iter

                    # test it on the test set
                    test_losses = [test_model(i) for i
                                   in range(n_test_batches)]
                    test_score = numpy.mean(test_losses)

                    print(('     epoch %i, minibatch %i/%i, test error of '
                           'best model %f %%') %
                          (epoch, minibatch_index + 1, n_train_batches,
                           test_score * 100.))
                    #save the best model


            if patience <= iter:
                done_looping = True
                break
    fid = open('savenet.data', 'wb')
    pickle.dump(classifier.hiddenLayer.W, fid)
    pickle.dump(classifier.hiddenLayer.b, fid)
    pickle.dump(classifier.logRegressionLayer.W, fid)
    pickle.dump(classifier.logRegressionLayer.b, fid)
    fid.close()

    end_time = timeit.default_timer()
    print(('Optimization complete. Best validation score of %f %% '
           'obtained at iteration %i, with test performance %f %%') %
          (best_validation_loss * 100., best_iter + 1, test_score * 100.))
    print(('The code for file ' +
           os.path.split(__file__)[1] +
           ' ran for %.2fm' % ((end_time - start_time) / 60.)))



