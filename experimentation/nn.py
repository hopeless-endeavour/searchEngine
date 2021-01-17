import math 
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# class Layer:
#     def __init__(self, num_inputs, num_nodes):
#         self.weights = np.shape(num_inputs, num_nodes)
#         self.biases = np.zeros((1, num_nodes))
    
#     def forward(self, inputs):
#         self.output = np.dot(inputs, self.weights) + self.biases

#         return self.output

# def softmax(u):
#     """ applies softmax function to vector u""" 

#     expu = np.exp(u)
#     return expu/np.sum(expu)

# def cross_entropy(p,q):
#     """ applies cross_entropy function to probalbility vectors p and q."""

#     return -np.vdot(p,np.log(q))

# def logReg(X, Y, alpha):

#     epochs = 5
#     N, d = X.shape
#     beta = np.zeros((K, d+1))

#     for i in range

class LogisticRegression:
    
    def __init__(self, params,  alpha=0.0, max_iter=50000, flag=0):
        self.params = params
        self.alpha = alpha
        self.max_iter = max_iter
        self.flag = flag
    
    def _sigmoid(x):
        """ Sigmoid function """

        return 1.0 / (1.0 + np.exp(-x))
    
    def predict(self, x_bar, params):
        """ Predict the probability of a class """

        return  self._sigmoid(np.dot(params, x_bar))
    
    def _compute_cost(self, input_var, output_var, params):
        """ Compute the log likihood cost """

        cost = 0
        for x, y in zip(input_var, output_var):
            x_bar = np.array(np.insert(x,0,1))
            y_hat = self.predict(x_bar, params)
    
            y_bin = 1.0 if y == self.flag else 0.0
            cost += y_bin * np.log(y_hat) + (1 - y_bin) * np.log(1 - y_hat)

        return cost 

    def train(self, input_var, label, print_iter=5000):
        
        i = 1 
        while i < self.max_iter:
            if i % print_iter == 0:
                print(f'iteration: {i}')
                print(f'cost: {self._compute_cost(input_var, label, self.params)}')
                print("---------------------------------------------------------")
            for j, xy in enumerate(zip(input_var, label)):
                x_bar = np.array(np,insert(xy[0],0,1))
                y_hat = self.predict(x_bar, self.params)

                y_bin = 1.0 if xy[1] == self.flag else 0.0
                m = (y - y_hat) * x_bar
                self.params += self.alpha * m

            i += 1 

        return self.params, cost, params_store


    def test(self, input_test, label_test):
        self.total_classifications = 0
        self.correct_classifications = 0 

        for x,y in zip(input_test, label_test):
            self.total_classifications += 1
            x_bar = np.array(np,insert(x,0,1))
            y_hat = self.predict(x_bar, self.params)
            y_bin = 1.0 if y == self.flag else 0.0

            if y_hat >= 0.5 and y_bin == 1:
                # correct classification of class of interest 
                self.correct_classifications += 1
            
            if y_hat < 0.5 and y_bin != 1:
                # correct classification of class of interest 
                self.correct_classifications += 1

        self.accuracy = self.correct_classifications / self.total_classifications
            
                
        return self.accuracy 
    


