import numpy as np

def train_neural_network(X, Yd, num_inputs=32, num_hidden=16, num_outputs=4, epochsMax=100000, learnRate=0.1, Precis=0.001, save_path="trained_params.npy"):
    # Inicialización de pesos y umbrales
    W_input_hidden = np.random.uniform(-1, 1, (num_inputs, num_hidden))
    W_hidden_output = np.random.uniform(-1, 1, (num_hidden, num_outputs))
    umb_hidden = np.random.uniform(-1, 1, num_hidden)
    umb_output = np.random.uniform(-1, 1, num_outputs)

    # Función sigmoide
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    # Derivada de la sigmoide
    def sigmoid_derivative(x):
        return x * (1 - x)

    # Entrenamiento
    for epoch in range(epochsMax):
        errors = []
        for i in range(X.shape[0]):
            # Propagación hacia adelante
            hidden_input = np.dot(X[i], W_input_hidden) - umb_hidden
            hidden_output = sigmoid(hidden_input)

            final_input = np.dot(hidden_output, W_hidden_output) - umb_output
            final_output = sigmoid(final_input)

            # Cálculo del error
            error = Yd[i] - final_output
            errors.append(np.mean(error**2))

            # Backpropagation
            delta_output = error * sigmoid_derivative(final_output)
            delta_hidden = sigmoid_derivative(hidden_output) * np.dot(delta_output, W_hidden_output.T)

            # Gradientes
            W_hidden_output += learnRate * np.outer(hidden_output, delta_output)
            W_input_hidden += learnRate * np.outer(X[i], delta_hidden)
            umb_output += -learnRate * delta_output
            umb_hidden += -learnRate * delta_hidden

        # Criterio de parada
        mse = np.mean(errors)
        if mse < Precis:
            break

    # Guardar parámetros entrenados
    trained_params = {
        "W_input_hidden": W_input_hidden,
        "W_hidden_output": W_hidden_output,
        "umb_hidden": umb_hidden,
        "umb_output": umb_output,
    }
    np.save(save_path, trained_params)
    print(f"Parámetros guardados en: {save_path}")
