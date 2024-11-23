import os
import cv2
import numpy as np
#from motor_control import move_forward, stop_car, steer_with_rack_pinion, cleanup
from camera_processing import preprocess_frame
from nn_model import NeuralNetwork

# Mapeo de direcciones
DIRECTIONS = {
    0: "adelante",
    1: "derecha",
    2: "izquierda",
    3: "alto"
}

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

def train_model():
    # Configuración de datos
    DATA_DIR = r"C:\Users\LALO TORRES\Downloads\data" #Directorio de DATOS
    CLASSES = ["adelante", "derecha", "izquierda", "alto"]

    # Cargar datos
    print("Cargando datos de entrenamiento...")
    X_train, y_train = load_training_data(DATA_DIR, CLASSES)
    print(f"Datos cargados: {len(X_train)} imágenes")

    # Crear y entrenar modelo
    print("Entrenando el modelo...")
    model = NeuralNetwork(input_size=4096, hidden_size=64, output_size=4)
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

            # Controlar el carrito
            if direction == "adelante":
                move_forward()
            elif direction == "alto":
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
        


