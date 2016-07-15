import numpy as np
import theano
import theano.tensor as T

from nn.ActivationLayer import ActivationLayer
from nn.BatchNormLayer import BatchNormLayer
from nn.HiddenLayer import HiddenLayer
from nn.Network import Network
from nn.AdamTrainer import AdamTrainer

from tools.utils import load_mnist

rng = np.random.RandomState(23455)

datasets = load_mnist(rng)

shared = lambda d: theano.shared(d, borrow=True)

train_set_x, train_set_y = map(shared, datasets[0])
valid_set_x, valid_set_y = map(shared, datasets[1])
test_set_x, test_set_y   = map(shared, datasets[2])

network = Network(
    HiddenLayer(rng, (784, 500)),
    BatchNormLayer(rng, (784, 500)),
    ActivationLayer(rng, f='ReLU'),

    HiddenLayer(rng, (500, 10)),
    BatchNormLayer(rng, (500, 10)),
    ActivationLayer(rng, f='softmax')
)

trainer = AdamTrainer(rng=rng, batchsize=100, epochs=1, alpha=0.00001, cost='cross_entropy')
trainer.train(network=network, train_input=train_set_x, train_output=train_set_y,
                               valid_input=valid_set_x, valid_output=valid_set_y,
                               test_input=test_set_x, test_output=test_set_y, filename=None)