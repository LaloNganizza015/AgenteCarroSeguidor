import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Ruta de la carpeta de datos (ajusta esta ruta)
data_dir = r'D:\feroz\Descargas\data\data'

# Configuración de datos
batch_size = 32
img_size = (64, 64)

# Generadores de datos para entrenamiento y validación
datagen = ImageDataGenerator(rescale=1.0/255, validation_split=0.2)

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

# Construcción del modelo
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(64, 64, 3)),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(train_generator.num_classes, activation='softmax')  # Num. de clases
])

# Compilación del modelo
model.compile(optimizer=Adam(learning_rate=0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Entrenamiento del modelo
epochs = 100
model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=epochs
)

# Guardar el modelo entrenado
model.save('traffic_sign_model.h5')
print("Modelo entrenado y guardado como 'traffic_sign_model.h5'")

# Clases detectadas
print("Clases detectadas:", train_generator.class_indices)
