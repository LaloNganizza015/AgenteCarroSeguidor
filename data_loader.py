import os
import cv2
import numpy as np

# Función para cargar y preprocesar imágenes
def load_training_data(data_dir, classes, img_size=(32, 32)):
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
            X_train.append(img)
            y_train.append(label_map[class_name])

    X_train = np.array(X_train).reshape(-1, img_size[0], img_size[1], 1)
    y_train = np.array(y_train)

    return X_train, y_train
