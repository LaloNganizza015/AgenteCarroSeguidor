import RPi.GPIO as GPIO # Importa la biblioteca GPIO para manejo de los pines de la Raspberry PI
import time # Importa la biblioteca tiempo para la obtencion de fecha y hora

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
velocidad_general = 60  # Controla la velocidad general del carro

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
         GPIO.output(motor_del_izq_B, GPIO.LOW)  # Adelante
         pwm_del_izq.ChangeDutyCycle(velocidad_izq)
     else:
         GPIO.output(motor_tras_izq_B, GPIO.HIGH)  # Reversa
         pwm_tras_izq.ChangeDutyCycle(abs(velocidad_izq))
         GPIO.output(motor_del_izq_B, GPIO.HIGH)  # Reversa
         pwm_del_izq.ChangeDutyCycle(abs(velocidad_izq))

     if velocidad_der > 0:
         GPIO.output(motor_tras_der_B, GPIO.LOW)  # Adelante
         pwm_tras_der.ChangeDutyCycle(velocidad_der)
         GPIO.output(motor_del_der_B, GPIO.LOW)  # Adelante
         pwm_del_der.ChangeDutyCycle(velocidad_der)
     else:
         GPIO.output(motor_tras_der_B, GPIO.HIGH)  # Reversa
         pwm_tras_der.ChangeDutyCycle(abs(velocidad_der))
         GPIO.output(motor_del_der_B, GPIO.HIGH)  # Reversa
         pwm_del_der.ChangeDutyCycle(abs(velocidad_der))


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

# Función para avanzar durante 2 segundos
def avanzar2seg():
    print("Avanzando...")
    controlar_motores_delanteros('avanzar')
    controlar_motores_traseros('avanzar')
    time.sleep(1)  # Avanza durante 2 segundos
    detener_carro()  # Detener el carro al finalizar

# Función para dar vuelta hacia izquierda o derecha
def vuelta(sentido, velocidad):
    if velocidad <= 0:
        print("La velocidad debe ser mayor que 0.")
        return
    
    # Tiempos base para cada sentido al 20% de velocidad
    tiempo_base_derecha = 2  # Tiempo necesario para girar a la derecha al 20%
    tiempo_base_izquierda = 2  # Tiempo necesario para girar a la izquierda al 20%
    
    if sentido.lower() == "izquierda":
        # Calcular tiempo de giro ajustado a la velocidad
        tiempo_giro = tiempo_base_izquierda * (20 / velocidad)
        print(f"Girando a la izquierda con velocidad {velocidad}%... Tiempo de giro: {tiempo_giro:.2f} segundos")
        servo.ChangeDutyCycle(3)  # Posicion hacia la izquierda
        ajustar_velocidades(5)  # Reducir velocidad en el lado izquierdo
        time.sleep(tiempo_giro)  # Tiempo de giro ajustado
    elif sentido.lower() == "derecha":
        # Calcular tiempo de giro ajustado a la velocidad
        tiempo_giro = tiempo_base_derecha * (20 / velocidad)
        print(f"Girando a la derecha con velocidad {velocidad}%... Tiempo de giro: {tiempo_giro:.2f} segundos")
        servo.ChangeDutyCycle(12)  # Posicion hacia la derecha
        ajustar_velocidades(-5)  # Reducir velocidad en el lado derecho
        time.sleep(tiempo_giro)  # Tiempo de giro ajustado
    else:
        print("Sentido invalido. Use 'izquierda' o 'derecha'.")
        return
    
    # Regresar a la posicion neutral y detener el ajuste de velocidades
    servo.ChangeDutyCycle(7.5)  # Regresar a la posicion neutral
    ajustar_velocidades(0)  # Restablecer velocidades tras el giro

    
    
def prueba():
    try:
        while True:
            avanzar2seg()  # Avanza durante 2 segundos
            vuelta("derecha", velocidad_general)  # Gira a la izquierda
            avanzar2seg()  # Avanza durante 2 segundos
            vuelta("izquierda", velocidad_general)  # Gira a la derecha
    except KeyboardInterrupt:
        print("Prueba finalizada por el usuario.")
        detener_carro()  # Detener el carro
        pwm_del_izq.stop()  # Detiene la emisión de los pulsos de PWM
        pwm_del_der.stop()
        pwm_tras_izq.stop()
        pwm_tras_der.stop()
        servo.ChangeDutyCycle(7.5)
        time.sleep(1)
        servo.stop()  # Detiene la emisión de los pulsos de PWM
        GPIO.cleanup()  # Limpia todas las salidas y alarmas correspondientes al GPIO
  
# Llamada de la función para comenzar la tarea de seguidor de linea
prueba()
