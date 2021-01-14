import math 
import numpy as np
import matplotlib.pyplot as plt

class Layer:
    def __init__(self, num_inputs, num_nodes):
        self.weights = np.shape(num_inputs, num_nodes)
        self.biases = np.zeros((1, num_nodes))
    
    def forward(self, inputs):
        self.output = np.dot(inputs, self.weights) + self.biases

        return self.output

def softmax(u):
    """ applies softmax function to vector u""" 

    expu = np.exp(u)
    return expu/np.sum(expu)

def cross_entropy(p,q):
    """ applies cross_entropy function to probalbility vectors p and q."""

    return -np.vdot(p,np.log(q))

def logReg(X, Y, alpha):

    epochs = 5
    N, d = X.shape
    beta = np.zeros((K, d+1))

    for i in range