import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import Picamera2, Preview
import time
import cv2

# Cargar el modelo TensorFlow Lite
#interpreter = tflite.Interpreter(model_path="redNeuronal_triangulo500.tflite")
interpreter = tflite.Interpreter(model_path="redNeuronalfere.tflite")
interpreter.allocate_tensors()

# Obtener detalles de entrada y salida
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Clases detectadas (ajusta según tu modelo)
class_names = {0: 'adelante', 1: 'alto', 2: 'derecha', 3: 'izquierda'}

# Preprocesar la imagen de entrada
def preprocess_image(frame):
    try:
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convertir a RGB
        img = cv2.resize(img, (224, 224))  # Cambiar tamaño
        img = img / 255.0  # Normalizar
        img = np.expand_dims(img, axis=0).astype(np.float32)  # Añadir batch dimension
        return img
    except Exception as e:
        print(f"Error al preprocesar la imagen: {e}")
        return None

# Función para controlar procesos según la predicción
def controlar_proceso(predicted_class):
    if predicted_class == "adelante":
        print("Mover hacia adelante")
        # Código para mover motores
    elif predicted_class == "alto":
        print("Detener movimiento")
        # Código para detener
    elif predicted_class == "derecha":
        print("Girar a la derecha")
        # Código para girar
    elif predicted_class == "izquierda":
        print("Girar a la izquierda")
        # Código para girar
    else:
        print("Sin acción, clase 'ninguna'")

# Clasificar imágenes
def clasificar(imagen):
    try:
        interpreter.set_tensor(input_details[0]['index'], imagen)
        interpreter.invoke()
        predictions = interpreter.get_tensor(output_details[0]['index'])[0]
        
        # Obtener la clase con mayor probabilidad
        max_prob = np.max(predictions)
        if max_prob < 0.7:  # Umbral configurable
            predicted_class = "ninguna"
        else:
            class_idx = np.argmax(predictions)
            predicted_class = class_names.get(class_idx)
        
        # Mostrar predicción
        print(f'Predicción: {predicted_class} ({max_prob:.2f})')
        
        # Controlar procesos según predicción
        controlar_proceso(predicted_class)
        return predicted_class

    except Exception as e:
        print(f"Error durante la clasificación: {e}")
        return "ninguna"

# Configuración de la cámara y bucle principal
def main():
    picam = Picamera2()
    picam.start_preview(Preview.QTGL)
    picam.configure(picam.create_preview_configuration(main={"size": (640, 480)}))
    picam.start()

    try:
        while True:
            frame = picam.capture_array()
            imagen = preprocess_image(frame)
            if imagen is not None:
                clasificar(imagen)
            else:
                print("Error al preprocesar la imagen.")
            time.sleep(0.2)  # Ajusta el tiempo según lo necesario
    except KeyboardInterrupt:
        print("Ejecución detenida por el usuario.")
    finally:
        picam.close()
        print("Cámara cerrada.")

if __name__ == "__main__":
    main()
