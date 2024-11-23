import os
import cv2
import numpy as np

# Mapeo de direcciones
DIRECTIONS = {
    0: "adelante",
    1: "derecha",
    2: "izquierda",
    3: "reversa"
}

# Umbral de confianza para hacer una predicción
CONFIDENCE_THRESHOLD = 0.65

# Función para cargar datos de entrenamiento desde directorios
def load_training_data(data_dir, classes, img_size=(64, 64)):
    label_map = {label: idx for idx, label in enumerate(classes)}
    X_train = []
    y_train = []

    for class_name in classes:
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.isdir(class_dir):
            print(f"Directorio no encontrado: {class_dir}")
            continue

        for img_name in os.listdir(class_dir):
            img_path = os.path.join(class_dir, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                print(f"No se pudo cargar la imagen: {img_path}")
                continue

            img = cv2.resize(img, img_size)
            img = img / 255.0
            X_train.append(img.flatten())  # Convertimos en vector
            y_train.append(np.eye(len(classes))[label_map[class_name]])  # Etiqueta en formato one-hot

    X_train = np.array(X_train)
    y_train = np.array(y_train)
    return X_train, y_train

# Definición de la clase NeuralNetwork
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.W1 = np.random.randn(input_size, hidden_size)  # Pesos de la capa oculta
        self.b1 = np.zeros(hidden_size)  # Sesgos de la capa oculta
        self.W2 = np.random.randn(hidden_size, output_size)  # Pesos de la capa de salida
        self.b2 = np.zeros(output_size)  # Sesgos de la capa de salida

    def train(self, X_train, y_train, epochs=1000, learning_rate=0.01):
        for epoch in range(epochs):
            # Propagación hacia adelante
            hidden = np.dot(X_train, self.W1) + self.b1
            hidden = np.tanh(hidden)  # Función de activación

            output = np.dot(hidden, self.W2) + self.b2
            output = self.softmax(output)  # Softmax para la salida

            # Cálculo del error
            error = output - y_train

            # Retropropagación
            output_grad = error * self.softmax_derivative(output)
            hidden_grad = np.dot(output_grad, self.W2.T) * self.tanh_derivative(hidden)

            # Actualización de pesos y sesgos
            self.W2 -= learning_rate * np.dot(hidden.T, output_grad)
            self.b2 -= learning_rate * np.sum(output_grad, axis=0)
            self.W1 -= learning_rate * np.dot(X_train.T, hidden_grad)
            self.b1 -= learning_rate * np.sum(hidden_grad, axis=0)

            # Imprimir progreso de entrenamiento
            if epoch % 100 == 0:
                loss = np.mean(np.square(error))  # Error cuadrático medio
                print(f"Época {epoch}, Error: {loss}")

    def predict(self, X):
        hidden = np.dot(X, self.W1) + self.b1
        hidden = np.tanh(hidden)  # Función de activación
        output = np.dot(hidden, self.W2) + self.b2
        return self.softmax(output)

    def save_model(self, filename):
        np.savez(filename, W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2)

    @staticmethod
    def load_model(filename):
        data = np.load(filename)
        model = NeuralNetwork(data['W1'].shape[0], data['W1'].shape[1], data['W2'].shape[1])
        model.W1 = data['W1']
        model.b1 = data['b1']
        model.W2 = data['W2']
        model.b2 = data['b2']
        return model

    # Funciones de activación
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    def softmax_derivative(self, x):
        s = self.softmax(x)
        return s * (1 - s)

    def tanh_derivative(self, x):
        return 1.0 - np.tanh(x) ** 2


# Función para preprocesar las imágenes capturadas (blanco y negro)
def preprocess_frame(frame, img_size=(64, 64)):
    # Convertir la imagen a escala de grises
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplicar umbral para obtener la imagen en blanco y negro
    _, binary_frame = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY)
    
    # Detectar cuadrado dentro de la imagen
    square_roi = detect_square(binary_frame)
    
    # Si encontramos un cuadrado, recortar la región de interés (ROI)
    if square_roi is not None:
        x, y, w, h = square_roi
        cropped_frame = binary_frame[y:y+h, x:x+w]
        resized_frame = cv2.resize(cropped_frame, img_size)
    else:
        resized_frame = cv2.resize(binary_frame, img_size)
    
    normalized_frame = resized_frame / 255.0
    return normalized_frame.flatten()

# Función para detectar un cuadrado en la imagen binaria
def detect_square(binary_frame):
    # Detectar contornos en la imagen binaria
    contours, _ = cv2.findContours(binary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        # Aproximar el contorno para obtener un polígono
        epsilon = 0.04 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Si tiene 4 vértices, lo consideramos un cuadrado
        if len(approx) == 4:
            # Obtener las coordenadas del rectángulo que enmarca el cuadrado
            x, y, w, h = cv2.boundingRect(approx)
            return (x, y, w, h)
    return None

# Función para entrenar el modelo
def train_model():
    DATA_DIR = r"C:\Users\sebas\Music\Proyecto Carrito\data"  # Cambia este directorio
    CLASSES = ["adelante", "derecha", "izquierda", "reversa"]

    print("Cargando datos de entrenamiento...")
    X_train, y_train = load_training_data(DATA_DIR, CLASSES)
    print(f"Datos cargados: {len(X_train)} imágenes")

    print("Entrenando el modelo...")
    model = NeuralNetwork(input_size=4096, hidden_size=64, output_size=4)
    model.train(X_train, y_train, epochs=1000)
    model.save_model("nn_model.npz")
    print("Entrenamiento completado y modelo guardado.")

## Función principal para la predicción
def main():
    model = NeuralNetwork.load_model("nn_model.npz")
    print("Modelo cargado. Iniciando cámara...")

    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Vista en tiempo real", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):  # Capturar imagen con 's'
                input_data = preprocess_frame(frame)
                prediction = model.predict(input_data.reshape(1, -1))
                predicted_label = np.argmax(prediction)
                confidence = prediction[0][predicted_label]

                if confidence >= CONFIDENCE_THRESHOLD:
                    print(f"Dirección detectada: {DIRECTIONS[predicted_label]} (Confianza: {confidence:.2f})")
                else:
                    print("Señal no reconocida.")

            elif key == ord('q'):  # Salir con 'q'
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        
# Selección del modo

if __name__ == "__main__":
    mode = input("Selecciona el modo (train/predict): ").strip().lower()
    if mode == "train":
        train_model()
    elif mode == "predict":
        main()
    else:
        print("Modo no válido. Usa 'train' o 'predict'.")