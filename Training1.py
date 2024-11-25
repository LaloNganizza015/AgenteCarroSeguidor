import os
import numpy as np
import cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow as tf

# Ruta de la carpeta de datos (ajusta esta ruta)
data_dir = r'D:\feroz\Descargas\data\data'

# Configuración de datos
batch_size = 32
img_size = (128, 128)  # Aumentamos la resolución a 128x128

# Aumento de datos (Data Augmentation)
datagen = ImageDataGenerator(
    rescale=1.0/255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    brightness_range=[0.5, 1.5],  # Cambiar el brillo
    channel_shift_range=20.0  # Cambiar los valores de color
)

train_generator = datagen.flow_from_directory(
    data_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training'
)

val_generator = datagen.flow_from_directory(
    data_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation'
)

# Cargar modelo preentrenado VGG16 y agregar capas adicionales
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(128, 128, 3))  # Usamos imágenes más grandes
base_model.trainable = False  # Congelamos el modelo base inicialmente

# Construcción del modelo
model = Sequential([
    base_model,
    Flatten(),
    Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
    Dropout(0.5),
    Dense(train_generator.num_classes, activation='softmax')  # Número de clases
])

# Compilación del modelo con una tasa de aprendizaje pequeña
optimizer = Adam(learning_rate=0.0001)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

# Callbacks
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# Entrenamiento del modelo
epochs = 100  # Puedes aumentar las épocas si es necesario
model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=epochs,
    callbacks=[early_stopping]
)

# Guardar el modelo entrenado
model.save('redNeuronalfere.keras')
print("Modelo entrenado y guardado como 'redNeuronalfere.keras'")

# Clases detectadas
print("Clases detectadas:", train_generator.class_indices)
