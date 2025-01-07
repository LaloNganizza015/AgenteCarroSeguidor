import cv2 # Importa la biblioteca OPENCV para procesar imagenes
import pandas as pd # Importa la biblioteca PANDAS para crear el archivo .xlsx
import time # Importa la biblioteca tiempo para la obtencion de fecha y hora
import numpy as np # Importa la biblioteca numpy para operaciones numericas extensas
from picamera2 import Picamera2, Preview # Importa la biblioteca # Importa el modulo de la biblioteca para comunicar con el modulo de camara
import motor_control as mc
import Cudaros1_1 as cdds  # Modulo que contiene la funcion find_squares
from Clase_Cuadro import Cuadro
import LectSensor as LS
import Lite_ejecucion1 as LE1
import FuncionVuelta as FV

# Parametros de funcionamiento del vehiculo
# Parametro de velocidad general (ajustado entre 0 y 100)
velocidad_general = 18  # Controla la velocidad general del carro
# Umbral para detectar el cuadrado de las señales y empezar a avanzar
umbral = 12000
# Configuracion de porcentajes de area
MIN_AREA_PERCENT = 0.005  # Porcentaje minimo del area total
MAX_AREA_PERCENT = 0.70  # Porcentaje maximo del area total
# Parametro para detener el vehiculo frente a la señal
max_area = 300000
# Variable de inicio de recorrido
INICIO = False
# Variables a utilizar en el codigo principal
# Inicializar Variable puntos en 0 como Metrica de Rendimiento
puntos = 0
# Dimensiones de la captura de video
anc_cam = 640
alt_cam = 480

# Configuraciones iniciales
# Configuración para guardar datos en un archivo de Excel con los parametros de Acción tomada, Momento de la acción, Captura, Puntos por acción
df = pd.DataFrame(columns=['Acción', 'Timestamp', 'Imagen', 'Puntos'])
# Iniciar un hilo para manejar las ventanas de OpenCV
cv2.startWindowThread()
# Configurar la camara Raspberry Pi
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (anc_cam, alt_cam)}))
picam2.start()
# Captura del frame representando los pixeles de la imagen
frame = picam2.capture_array()   
frame_height, frame_width, _ = frame.shape  
total_area = frame_height * frame_width
min_area = MIN_AREA_PERCENT * total_area

# Función para obtener el centroide del cuadro
def obtener_centro(squares, areas, anc_cam, alt_cam):
    if not squares or not areas:  # Si no hay cuadrados detectados
        print("No se detectaron cuadrados.")
        return None

    # Seleccionar el cuadrado más grande
    max_index = np.argmax(areas)  # Índice del cuadrado con mayor área
    selected_square = squares[max_index]

    # Calcular el centroide del cuadrado seleccionado
    M = cv2.moments(selected_square)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
    else:
        cx, cy = 0, 0

    # Calcular el error entre el centro del cuadrado y el centro de la cámara
    camera_center_x = anc_cam // 2
    camera_center_y = alt_cam // 2
    error_x = camera_center_x - cx
    error_y = camera_center_y - cy

    # Calcular el área del cuadrado seleccionado
    max_area = areas[max_index]

    # Mostrar detalles del cuadrado seleccionado
    print(f"Centroide del cuadrado seleccionado: ({cx}, {cy}), Área: {max_area}, Error X: {error_x}, Error Y: {error_y}")

    # Retornar área, errores y cuadrado seleccionado
    return max_area, error_x, error_y


# Función para capturar y guardar imagen con la acción tomada
def registrar_accion_clas(accion, frame, puntos):
    timestamp = time.strftime("%Y%m%d-%H%M%S") # Registro del momento exacto de la decisión
    file_name = f'captura_{timestamp}.jpg' # Nombre de la captura correspondiente al momento
    cv2.imwrite(file_name, frame) # Toma de captura
    df.loc[len(df)] = [accion, timestamp, file_name, puntos]
    #Registro de la acción, momento de captura, nombre de la captura, puntuación actual.

# Función para capturar la acción tomada para corregir rumbo
def registrar_accion_mov(accion, puntos):
    df.loc[len(df)] = [accion, 0, 0, puntos]
    #Registro de la acción, puntuación actual.

# Función para seguir la línea
def iniciar_recorrido():
    global INICIO
    duty_cycle = 6.5
    duty_cycle1 = 7.5
    mc.inicializar_componentes()
    error_anterior = 0
    error_anteriory = 0
    global puntos  # Métrica de rendimiento
    while True:
        frame = picam2.capture_array()
        frame_with_squares, squares, areas = cdds.find_squares(frame, min_area, max_area)
        # Mostrar el frame con los cuadrados detectados
        cv2.imshow("Detected Squares", frame_with_squares)
        if INICIO:
            if squares:  # Si se detectan cuadrados
                result = obtener_centro(squares, areas, anc_cam, alt_cam)         
                if LS.monitorear_sensores():
                    mc.detener_carro()
                else:
                    if result:
                        area, error_x, error_y = result
                        print(f"area detectada: {area}, Umbral: {umbral}")
                        if area < umbral:  # Si el área es menor al umbral
                            print(f"Avanzando hacia la señal. Error X: {error_x}, Área: {area}")
                            # Calcular velocidad basada en el área detectada (mayor área, menor velocidad)
                            velocidad_ajustada = max(10, velocidad_general - int(area / 1500))
                            mc.controlar_direccion_cam2(error_y, error_anteriory, area)
                            error_anteriory = error_y
                            time.sleep(1)
                            mc.controlar_motores(velocidad_ajustada)
                            mc.controlar_direccion2(error_x, error_anterior, area)                        
                            #mc.ajustar_velocidades(error_x, velocidad_ajustada)
                            error_anterior = error_x
                            # Actualización de puntos y registro
                            if abs(error_x) < 10:
                                puntos += 4
                                registrar_accion_mov('Avanzar hacia adelante', puntos)
                            elif error_x > 10:
                                puntos -= 2
                                registrar_accion_mov('Corregir a la derecha', puntos)
                            elif error_x < -10:
                                puntos -= 2
                                registrar_accion_mov('Corregir a la izquierda', puntos)
                            time.sleep(0.5)
                        else:  # Si el área es suficiente, detener el vehículo
                            print("La señal ocupa el área deseada. Deteniendo.")
                            mc.detener_carro()
                            puntos += 4
                            time.sleep(1)
                            registrar_accion_clas('Clasificar imagen', frame, puntos)
                            img = LE1.preprocess_image(frame)
                            FV.prediccion(LE1.clasificar(img), velocidad_general, error_x)
                            time.sleep(1)
                    else:
                        print("No se pudo calcular el centro del cuadrado.")
            else:  # No se detectaron cuadrados
                print("No se detectó ninguna señal.")
                mc.reversa_carro(velocidad_general)
                time.sleep(0.5)
                mc.detener_carro()
                puntos -= 5
                registrar_accion_mov('Sin señal', puntos)
        # Salir del bucle con 'q', ajustar duty cycle con 'e' y 'r'
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('e'):
            duty_cycle += 0.5
            mc.CamDutyCycle(duty_cycle)
        elif key == ord('r'):
            duty_cycle -= 0.5
            mc.CamDutyCycle(duty_cycle)
        elif key == ord('a'):
            duty_cycle1 -= 1
            mc.DirDutyCycle(duty_cycle1)
            FV.avanzar1seg(velocidad_general)
        elif key == ord('d'):
            duty_cycle1 += 1
            mc.DirDutyCycle(duty_cycle1)
            FV.avanzar1seg(velocidad_general)
        elif key == ord('w'):
            mc.controlar_motores(velocidad_general)
        elif key == ord('s'):
            duty_cycle1 += 0.5
            mc.reversa_carro(velocidad_general)
        elif key == ord('i'):
            INICIO = not INICIO
        time.sleep(0.8)

    cv2.destroyAllWindows()
    mc.limpiar_gpio()
    df.to_excel('registro_acciones.xlsx', index=False)




# Llamada de la función para comenzar el recorrido
iniciar_recorrido()


