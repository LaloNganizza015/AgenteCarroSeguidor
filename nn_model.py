import numpy as np
import pickle  # Para guardar y cargar el modelo

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, lr=0.01):
        self.lr = lr
        self.weights_input_hidden = np.random.rand(input_size, hidden_size) - 0.5
        self.weights_hidden_output = np.random.rand(hidden_size, output_size) - 0.5
        self.bias_hidden = np.zeros(hidden_size)
        self.bias_output = np.zeros(output_size)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def predict(self, X):
        hidden_input = np.dot(X, self.weights_input_hidden) + self.bias_hidden
        hidden_output = self.sigmoid(hidden_input)
        final_input = np.dot(hidden_output, self.weights_hidden_output) + self.bias_output
        return self.sigmoid(final_input)

    def train(self, X, y, epochs=1000):
        for epoch in range(epochs):
            # Forward pass
            hidden_input = np.dot(X, self.weights_input_hidden) + self.bias_hidden
            hidden_output = self.sigmoid(hidden_input)
            final_input = np.dot(hidden_output, self.weights_hidden_output) + self.bias_output
            output = self.sigmoid(final_input)

            # Error
            error = y - output

            # Backpropagation
            output_gradient = error * self.sigmoid_derivative(output)
            hidden_error = np.dot(output_gradient, self.weights_hidden_output.T)
            hidden_gradient = hidden_error * self.sigmoid_derivative(hidden_output)

            # Update weights and biases
            self.weights_hidden_output += self.lr * np.dot(hidden_output.T, output_gradient)
            self.bias_output += self.lr * np.sum(output_gradient, axis=0)
            self.weights_input_hidden += self.lr * np.dot(X.T, hidden_gradient)
            self.bias_hidden += self.lr * np.sum(hidden_gradient, axis=0)

    def save_model(self, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_model(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)
