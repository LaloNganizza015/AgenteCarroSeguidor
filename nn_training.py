import numpy as np
from TrainNNSencilla import train_neural_network


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

    def train(self, X, y, epochs):
        for epoch in range(epochs):
            for xi, yi in zip(X, y):
                # Forward pass
                hidden_input = np.dot(xi, self.weights_input_hidden) + self.bias_hidden
                hidden_output = self.sigmoid(hidden_input)
                final_input = np.dot(hidden_output, self.weights_hidden_output) + self.bias_output
                final_output = self.sigmoid(final_input)

                # Compute error
                output_error = yi - final_output
                hidden_error = np.dot(output_error, self.weights_hidden_output.T) * self.sigmoid_derivative(hidden_output)

                # Backpropagation
                self.weights_hidden_output += self.lr * np.outer(hidden_output, output_error)
                self.bias_output += self.lr * output_error
                self.weights_input_hidden += self.lr * np.outer(xi, hidden_error)
                self.bias_hidden += self.lr * hidden_error
            
            if (epoch + 1) % 10 == 0:
                loss = np.mean((output_error) ** 2)
                print(f"Epoch {epoch+1}, Loss: {loss:.4f}")

    def predict(self, X):
        hidden_input = np.dot(X, self.weights_input_hidden) + self.bias_hidden
        hidden_output = self.sigmoid(hidden_input)
        final_input = np.dot(hidden_output, self.weights_hidden_output) + self.bias_output
        return self.sigmoid(final_input)

if __name__ == "__main__":
    from preprocessing import load_and_preprocess_images

    # Cargar datos
    X, y = load_and_preprocess_images("dataset")
    y_one_hot = np.eye(4)[y]  # Convertir etiquetas a one-hot

    # Crear y entrenar la red
    nn = NeuralNetwork(input_size=1024, hidden_size=64, output_size=4)
    nn.train(X, y_one_hot, epochs=100)


# Datos de entrada y salida
X = np.random.randint(0, 2, (16, 32))  # 16 muestras, 32 entradas binarias
Yd = np.random.randint(0, 2, (16, 4))  # 16 muestras, 4 salidas deseadas

# Entrenar y guardar los parámetros en un archivo
train_neural_network(X, Yd, save_path="trained_params.npy")