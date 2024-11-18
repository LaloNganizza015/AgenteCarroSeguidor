import cv2
import numpy as np
from motor_control import move_forward, stop_car, steer_with_rack_pinion, cleanup
from camera_processing import preprocess_frame
from nn_model import NeuralNetwork
from EvalNNSencilla import evaluate_neural_network

# Mapeo de direcciones
DIRECTIONS = {
    0: "right",
    1: "left",
    2: "forward",
    3: "stop"
}

def train_model():
    # Cargar datos de entrenamiento (simulado)
    X_train = []  # Aquí irán las imágenes preprocesadas
    y_train = []  # Aquí irán las etiquetas

    # Simulación: cargar datos desde directorios
    for label, direction in DIRECTIONS.items():
        for i in range(100):  # Simular 100 imágenes por clase
            img = np.random.rand(32, 32)  # Reemplaza con la carga real de imágenes
            X_train.append(img.flatten())
            y_train.append(np.eye(4)[label])  # Etiqueta en formato one-hot

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # Crear y entrenar modelo
    model = NeuralNetwork(input_size=1024, hidden_size=64, output_size=4)
    model.train(X_train, y_train, epochs=1000)
    model.save_model("nn_model.pkl")
    print("Entrenamiento completado y modelo guardado.")

def main():
    # Cargar modelo entrenado
    model = NeuralNetwork.load_model("nn_model.pkl")
    print("Modelo cargado. Iniciando cámara...")

    cap = cv2.VideoCapture(0)  # Abrir cámara

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Preprocesar el frame
            input_data = preprocess_frame(frame)

            # Predecir el símbolo
            prediction = model.predict(input_data)
            predicted_label = np.argmax(prediction)
            direction = DIRECTIONS[predicted_label]
            
            # Esta red esta hecha sin bibliotecas para NN, usarla solo devuelve un valor numerico que debe ser evaluado
            
            # output = evaluate_neural_network(X_sample, load_path="trained_params.npy")
            # print(f"Salida de la red para la muestra: {output}")

            # Controlar el carrito
            if direction == "forward":
                move_forward()
            elif direction == "stop":
                stop_car()
            else:
                steer_with_rack_pinion(direction)

            # Mostrar predicción en la ventana
            cv2.putText(frame, f"Prediction: {direction}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Car Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        cleanup()

if __name__ == "__main__":
    mode = input("Selecciona el modo (train/predict): ").strip().lower()
    if mode == "train":
        train_model()
    elif mode == "predict":
        main()
    else:
        print("Modo no válido. Usa 'train' o 'predict'.")
