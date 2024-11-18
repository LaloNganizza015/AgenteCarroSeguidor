import numpy as np

def evaluate_neural_network(X_sample, load_path="trained_params.npy"):
    # Función sigmoide
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    # Cargar parámetros entrenados
    trained_params = np.load(load_path, allow_pickle=True).item()
    W_input_hidden = trained_params["W_input_hidden"]
    W_hidden_output = trained_params["W_hidden_output"]
    umb_hidden = trained_params["umb_hidden"]
    umb_output = trained_params["umb_output"]

    # Evaluación de la muestra
    hidden_output = sigmoid(np.dot(X_sample, W_input_hidden) - umb_hidden)
    final_output = sigmoid(np.dot(hidden_output, W_hidden_output) - umb_output)
    return final_output
