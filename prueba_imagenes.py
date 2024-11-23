import cv2
import numpy as np
import os

# Directorio donde se encuentran las imágenes
image_dir = r"C:\Users\LALO TORRES\Downloads\data"

X_train = []
y_train = []

# Mapeo de direcciones
DIRECTIONS = {
    0: "adelante",
    1: "derecha",
    2: "izquierda",
    3: "alto"
}

# Cargar las imágenes
for label, direction in DIRECTIONS.items():
    for filename in os.listdir(os.path.join(image_dir, direction)):
        img_path = os.path.join(image_dir, direction, filename)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (64, 64))  # Redimensionar a 64x64
        img = img.flatten()  # Aplana la imagen
        X_train.append(img)
        y_train.append(np.eye(4)[label])  # Etiqueta en formato one-hot

X_train = np.array(X_train)
y_train = np.array(y_train)

print(f"X_train shape: {X_train.shape}")
print(f"y_train shape: {y_train.shape}")

