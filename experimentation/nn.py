import math 
import numpy 

class Layer:
    def __init__(self, num_inputs, num_nodes):
        self.weights = np.shape(num_inputs, num_nodes)
        self.biases = np.zeros((1, num_nodes))
    
    def forward(self, inputs):
        self.output = np.dot(inputs, self.weights) + self.biases

        return self.output

layer1 = Layer()