# Codigo de Agente de Visión Artificial Equipo 5

import cv2 # Importa la biblioteca OPENCV para procesar imagenes
import pandas as pd # Importa la biblioteca PANDAS para crear el archivo .xlsx
import RPi.GPIO as GPIO # Importa la biblioteca GPIO para manejo de los pines de la Raspberry PI
import time # Importa la biblioteca tiempo para la obtencion de fecha y hora
from picamera2 import Picamera2, Preview # Importa la biblioteca # Importa el modulo de la biblioteca para comunicar con el modulo de camara

# Configuración de pines GPIO utilizando la numeracion de los GPIO
# Salida del servomotor de dirección
servo_pin = 18

# Salida de motores delanteros
motor_del_izq_A = 17
motor_del_izq_B = 27
motor_del_der_A = 22
motor_del_der_B = 10

# Salida de motores traseros
motor_tras_izq_A = 23
motor_tras_izq_B = 24
motor_tras_der_A = 7
motor_tras_der_B = 8

# Parámetro de velocidad general (ajustado entre 0 y 100)
velocidad_general = 70  # Controla la velocidad general del carro

# Inicializar GPIO
GPIO.setmode(GPIO.BCM) # Numeración de GPIO, diferente a la de PCB

# Configuración de los pines como salidas
# Configuración de servomotor de dirección
GPIO.setup(servo_pin, GPIO.OUT) 

# Configuración de motores delanteros
GPIO.setup(motor_del_izq_A, GPIO.OUT) # Motor izquierdo
GPIO.setup(motor_del_izq_B, GPIO.OUT)
GPIO.setup(motor_del_der_A, GPIO.OUT) # Motor derecho
GPIO.setup(motor_del_der_B, GPIO.OUT)

# Configuración de motores traseros
GPIO.setup(motor_tras_izq_A, GPIO.OUT) # Motor izquierdo
GPIO.setup(motor_tras_izq_B, GPIO.OUT)
GPIO.setup(motor_tras_der_A, GPIO.OUT) # Motor derecho
GPIO.setup(motor_tras_der_B, GPIO.OUT)

# Inicializar PWM para el servomotor de dirección
servo = GPIO.PWM(servo_pin, 50)  # Frecuencia de PWM de 50Hz
servo.start(7.5)  # Posición neutral del servo

# Inicializar PWM para los motores delanteros
pwm_del_izq = GPIO.PWM(motor_del_izq_A, 100)  # Frecuencia de PWM izquierdo de 100Hz
pwm_del_der = GPIO.PWM(motor_del_der_A, 100)  # Frecuencia de PWM derecho de 100Hz
pwm_del_izq.start(0)  # Ciclo de trabajo inicializado en 0
pwm_del_der.start(0)  # Ciclo de trabajo inicializado en 0

# Inicializar PWM para los motores traseros
pwm_tras_izq = GPIO.PWM(motor_tras_izq_A, 100)  # Frecuencia de PWM izquierdo de 100Hz
pwm_tras_der = GPIO.PWM(motor_tras_der_A, 100)  # Frecuencia de PWM derecho de 100Hz
pwm_tras_izq.start(0)  # Ciclo de trabajo inicializado en 0
pwm_tras_der.start(0)  # Ciclo de trabajo inicializado en 0

# Configuración para guardar datos en un archivo de Excel con los parametros de Acción tomada, Momento de la acción, Captura, Puntos por acción
df = pd.DataFrame(columns=['Acción', 'Timestamp', 'Imagen', 'Puntos'])

# Inicializar Variable puntos en 0 como Metrica de Rendimiento
puntos = 0

# Inicializar la camara con la biblioteca de Picamera2 
picam2 = Picamera2()
# Cambiar la resolución de captura y formato RGB
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()

# Función para capturar y guardar imagen con la acción tomada
def registrar_accion(accion, frame, puntos):
    timestamp = time.strftime("%Y%m%d-%H%M%S") # Registro del momento exacto de la decisión
    file_name = f'captura_{timestamp}.jpg' # Nombre de la captura correspondiente al momento
    cv2.imwrite(file_name, frame) # Toma de captura
    df.loc[len(df)] = [accion, timestamp, file_name, puntos]
    # Registro de la acción, momento de captura, nombre de la captura, puntuación actual.

# Función para obtener el centroide de la línea
def obtener_centroide(imagen_binarizada):
    momentos = cv2.moments(imagen_binarizada) # Obtenemos los momentos de la imagen creando un objeto de esta clase
    if momentos["m00"] != 0:
        # Si se detecta un area de pixeles blancos m00 es distinto de 0, de lo contrario la camara no percibe algo relevante en la imagen.
        cx = int(momentos["m10"] / momentos["m00"])
        # Encontramos la coordenada X del centroide de la figura mediante la division de momentos: sumatoria de posiciones sobre area total.
        return cx # Devuelve la coordenada
    else:
        return None # En caso de no haber areas de pixeles blancos

# Controlador PD para la dirección
def controlar_direccion(error, error_anterior):
    Kp = 0.04  # Ganancia proporcional
    Kd = 0.01  # Ganancia derivativa

    parte_proporcional = Kp * error
    derivada_error = (error - error_anterior) / 0.1
    parte_derivativa = Kd * derivada_error

    correccion = parte_proporcional + parte_derivativa
    duty_cycle = max(5, min(10, 7.5 - correccion))
    servo.ChangeDutyCycle(duty_cycle)

# Funcion para el control diferencial virtual
def ajustar_velocidades(error):
     ajuste = error * 0.1  # Ajuste basado en el error

     # Calcular los ciclos de trabajo para cada rueda
     velocidad_izq = max(0, min(100, velocidad_general + ajuste))
     velocidad_der = max(0, min(100, velocidad_general - ajuste))

     # Establecer la dirección y velocidad de las ruedas traseras
     # Esta parte fue añadida para evitar inversion de giro de los motores
     if velocidad_izq > 0:
         GPIO.output(motor_tras_izq_B, GPIO.LOW)  # Adelante
         pwm_tras_izq.ChangeDutyCycle(velocidad_izq)
     else:
         GPIO.output(motor_tras_izq_B, GPIO.HIGH)  # Reversa
         pwm_tras_izq.ChangeDutyCycle(abs(velocidad_izq))

     if velocidad_der > 0:
         GPIO.output(motor_tras_der_B, GPIO.LOW)  # Adelante
         pwm_tras_der.ChangeDutyCycle(velocidad_der)
     else:
         GPIO.output(motor_tras_der_B, GPIO.HIGH)  # Reversa
         pwm_tras_der.ChangeDutyCycle(abs(velocidad_der))


# Control de los motores delanteros
def controlar_motores_traseros(accion):
    if accion == 'avanzar':
        GPIO.output(motor_tras_izq_B, GPIO.LOW)
        GPIO.output(motor_tras_der_B, GPIO.LOW)

        # Ajustar PWM según la velocidad general
        pwm_tras_izq.ChangeDutyCycle(velocidad_general)
        pwm_tras_der.ChangeDutyCycle(velocidad_general)

# Control de los motores delanteros
def controlar_motores_delanteros(accion):
    if accion == 'avanzar':
        GPIO.output(motor_del_izq_B, GPIO.LOW)
        GPIO.output(motor_del_der_B, GPIO.LOW)

        # Ajustar PWM según la velocidad general
        pwm_del_izq.ChangeDutyCycle(velocidad_general)
        pwm_del_der.ChangeDutyCycle(velocidad_general)

# Detener el carro
def detener_carro():
    pwm_del_izq.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_del_der.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_tras_izq.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_tras_der.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0

# Función para seguir la línea
def seguir_linea():
    error_anterior = 0 # Inicializar valores en 0
    global puntos # Variable global para Metrica de rendimiento

    # Inicio del bucle principal
    while True:
        frame = picam2.capture_array() # Captura del frame representando los pixeles de la imagen
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Pasar la imagen a una escala de grises
        _, binarizada = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        # Se binariza la imagen de escala de grises en base a su intensidad y se invierte para que cualquier figura relevante
        # se ilumine de blanco y el entorno gris, el valor que define la intensidad es de 100

        centroide_x = obtener_centroide(binarizada) # Llamamos la función para encontrar el centroide en X de la imagen
        centro_imagen = frame.shape[1] // 2 # Partimos la imagen completa capturada en 2 para saber cual es el centro del carro

        if centroide_x is not None: # El centroide X debe estar definido
            error = centro_imagen - centroide_x # Definimos el error entre el centro de la imagen y el centro de la figura
            controlar_direccion(error, error_anterior) # Ajustamos la direccion del servomotor en base al error
            #ajustar_velocidades(error)
            controlar_motores_delanteros('avanzar') # Llama la función para arrancar motores delanteros
            controlar_motores_traseros('avanzar') # Llama la función para arrancar motores traseros

            if abs(error) < 10: # Si el error es menor a 10 pixeles
                puntos += 10 # Se suman 10 puntos a las metricas de rendimiento
                registrar_accion('Avanzar hacia adelante', frame, puntos) # Se registra la acción al dataframe
            elif error > 10: # Si el error es mayor a 10 pixeles
                puntos -= 2 # Se restan 2 puntos a la metrica de rendimiento
                registrar_accion('Girar a la derecha', frame, puntos) # Se registra la acción al dataframe
            elif error < -10: # Si el error es mayor a 10 pixeles en sentido contrario
                puntos -= 2 # Se restan 2 puntos a la metrica de rendimiento
                registrar_accion('Girar a la izquierda', frame, puntos) # Se registra la acción al dataframe

            error_anterior = error # Error anterior se le asigna el valor del error que ya fue utilizado para el control PD
        else:
            detener_carro() # Detiene el carro en caso de no estar definido el centroide en X
            puntos -= 5 # Se restan 5 puntos a la Metrica de rendimiento
            registrar_accion('Detenerse', frame, puntos) # Se registra la acción al dataframe

        cv2.imshow("Vista", binarizada) # Crea una ventana de la imagen binarizada
        if cv2.waitKey(1) & 0xFF == ord('q'): # Termina la ventana si en la ventana de imagen se presiona la tecla "q"
            break # Termina el bucle en caso de ser verdadero

    cv2.destroyAllWindows() # Destruye las ventanas creadas
    pwm_del_izq.stop() # Detiene la emisión de los pulsos de PWM
    pwm_del_der.stop() # Detiene la emisión de los pulsos de PWM
    pwm_tras_izq.stop() # Detiene la emisión de los pulsos de PWM
    pwm_tras_der.stop() # Detiene la emisión de los pulsos de PWM
    servo.stop() # Detiene la emisión de los pulsos de PWM
    GPIO.cleanup() # Limpia todas las salidas y alarmas correspondientes al GPIO
    df.to_excel('registro_acciones.xlsx', index=False) # Guarda el dataframe en un archivo .xlsx

# Llamada de la función para comenzar la tarea de seguidor de linea
seguir_linea()
