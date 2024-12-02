import cv2 # Importa la biblioteca OPENCV para procesar imagenes
import pandas as pd # Importa la biblioteca PANDAS para crear el archivo .xlsx
import RPi.GPIO as GPIO # Importa la biblioteca GPIO para manejo de los pines de la Raspberry PI
import time # Importa la biblioteca tiempo para la obtencion de fecha y hora
import numpy # Importa la biblioteca numpy para operaciones numericas extensas
from picamera2 import Picamera2, Preview # Importa la biblioteca # Importa el modulo de la biblioteca para comunicar con el modulo de camara
import motor_control as mc
import Cudaros as cdds  # Modulo que contiene la funcion find_squares

# Parámetro de velocidad general (ajustado entre 0 y 100)
velocidad_general = 20  # Controla la velocidad general del carro

# Umbral para detectar el cuadrado de las señales y empezar a avanzar
umbral = 160000

anc_cam = 640
alt_cam = 480

# Configuración para guardar datos en un archivo de Excel con los parametros de Acción tomada, Momento de la acción, Captura, Puntos por acción
df = pd.DataFrame(columns=['Acción', 'Timestamp', 'Imagen', 'Puntos'])

# Inicializar Variable puntos en 0 como Metrica de Rendimiento
puntos = 0

# Configuracion de porcentajes de area
MIN_AREA_PERCENT = 0.01  # Porcentaje minimo del area total (por ejemplo, 1%)
MAX_AREA_PERCENT = 0.10  # Porcentaje maximo del area total (por ejemplo, 10%)

# Iniciar un hilo para manejar las ventanas de OpenCV
cv2.startWindowThread()

# Configurar la camara Raspberry Pi
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

frame = picam2.capture_array() # Captura del frame representando los pixeles de la imagen   
frame_height, frame_width, _ = frame.shape  
total_area = frame_height * frame_width
min_area = MIN_AREA_PERCENT * total_area
max_area = MAX_AREA_PERCENT * total_area

# Función para obtener el centroide del cuadro
def obtener_centro(ancho_cam, alto_cam, umbral_area=0.9):
    frame = picam2.capture_array() # Captura del frame representando los pixeles de la imagen  
    squares = cdds.find_squares(frame, min_area, max_area)  # Obtener cuadrados detectados
    for square in squares:
        # Calcula el momento para hallar el centroide
        M = cv2.moments(square)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = 0, 0
        
        # Calcula el centro de la cámara
        camera_center_x = ancho_cam // 2
        camera_center_y = alto_cam // 2
        
        # Calcula el error entre el centro del cuadrado y el centro de la cámara
        error_x = camera_center_x - cx
        error_y = camera_center_y - cy
        
        # Verifica si el cuadrado ocupa el área deseada
        camera_area = ancho_cam * alto_cam
        #should_continue = max_area / camera_area < umbral_area
        should_continue = max_area < umbral_area
        return (error_x, error_y), should_continue
    else:
        # No se detectó ningún cuadrado
        return None, True

# Función para capturar y guardar imagen con la acción tomada
def registrar_accion(accion, frame, puntos):
    timestamp = time.strftime("%Y%m%d-%H%M%S") # Registro del momento exacto de la decisión
    file_name = f'captura_{timestamp}.jpg' # Nombre de la captura correspondiente al momento
    cv2.imwrite(file_name, frame) # Toma de captura
    df.loc[len(df)] = [accion, timestamp, file_name, puntos]
    # Registro de la acción, momento de captura, nombre de la captura, puntuación actual.


# Función para seguir la línea
def iniciar_recorrido():
    mc.inicializar_componentes()
    error_anterior = 0 # Inicializar valores en 0
    global puntos # Variable global para Metrica de rendimiento

    
    # Bucle para capturar y procesar cuadros en tiempo real
    while True:
        # Capturar un cuadro desde la camara
        frame = picam2.capture_array()

        # Calcular el area total de la imagen
        frame_height, frame_width, _ = frame.shape
        total_area = frame_height * frame_width

        # Convertir los porcentajes en valores absolutos de area
        min_area = MIN_AREA_PERCENT * total_area
        max_area = MAX_AREA_PERCENT * total_area

        # Detectar y dibujar cuadrados en el cuadro actual
        processed_frame = cdds.find_squares(frame, min_area, max_area)

        # Mostrar el cuadro procesado en una ventana
        cv2.imshow("Detected Squares", processed_frame)
        
        # Inicio del bucle principal
        
        (error, should_continue) = obtener_centro(anc_cam, alt_cam, umbral)
        if error is not None:
            error_x, error_y = error
            if should_continue:
                print(f"Avanzando. Error X: {error_x}, Error Y: {error_y}")
                # Aquí llamas a tus funciones de movimiento
                mc.controlar_motores_traseros(velocidad_general)
                mc.controlar_motores_delanteros(velocidad_general)
                mc.controlar_direccion(error_x, error_anterior)
                mc.ajustar_velocidades(error_x, velocidad_general)
                error_anterior = error_x # Error anterior se le asigna el valor del error que ya fue utilizado para el control PD
                if abs(error_x) < 10: # Si el error es menor a 10 pixeles
                    puntos += 4 # Se suman 10 puntos a las metricas de rendimiento
                    registrar_accion('Avanzar hacia adelante', frame, puntos) # Se registra la acción al dataframe
                elif error_x > 10: # Si el error es mayor a 10 pixeles
                    puntos -= 2 # Se restan 2 puntos a la metrica de rendimiento
                    registrar_accion('Corregir a la derecha', frame, puntos) # Se registra la acción al dataframe
                elif error_x < -10: # Si el error es mayor a 10 pixeles en sentido contrario
                    puntos -= 2 # Se restan 2 puntos a la metrica de rendimiento
                    registrar_accion('Corregir a la izquierda', frame, puntos) # Se registra la acción al dataframe
            else:
                print("El cuadrado ocupa el área deseada. Deteniendo.")
                mc.detener_carro()
                puntos += 4
                registrar_accion('Clasificar imagen', frame, puntos) # Se registra la acción al dataframe
                # Funcion para clasificar la imagen mostrada
                #respuesta = clasificacionRedNeuronal(binarizada)
                #Accion(respuesta)
                print('Clasificando señal')
        else:
            print("No se detectó ningún cuadrado.")
            puntos -= 5 # Se restan 5 puntos a la Metrica de rendimiento
            registrar_accion('Sin señal', frame, puntos) # Se registra la acción al dataframe
        mc.stop_servo_cam()
        print("Vista binarizada")    
        #cv2.imshow("Vista", binarizada) # Crea una ventana de la imagen binarizada

        # Salir del bucle al presionar la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows() # Destruye las ventanas creadas
    mc.limpiar_gpio()
    df.to_excel('registro_acciones.xlsx', index=False) # Guarda el dataframe en un archivo .xlsx
# Llamada de la función para comenzar el recorrido
iniciar_recorrido()

# Liberar los recursos y cerrar las ventanas
cv2.destroyAllWindows()

