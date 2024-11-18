import cv2
import numpy as np
import os

def load_and_preprocess_images(image_folder, img_size=(32, 32)):
    images = []
    labels = []
    classes = {'right': 0, 'left': 1, 'forward': 2, 'stop': 3}
    
    for label, class_id in classes.items():
        class_folder = os.path.join(image_folder, label)
        for file in os.listdir(class_folder):
            img_path = os.path.join(class_folder, file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                img = cv2.resize(img, img_size)
                img = img / 255.0  # Normalización
                images.append(img.flatten())  # Aplanar para la red
                labels.append(class_id)
    
    return np.array(images), np.array(labels)

if __name__ == "__main__":
    # Prueba del script
    images, labels = load_and_preprocess_images("dataset")
    print(f"Imágenes cargadas: {images.shape}, Etiquetas: {labels.shape}")
