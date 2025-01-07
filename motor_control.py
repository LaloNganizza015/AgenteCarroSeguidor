import RPi.GPIO as GPIO # Importa la biblioteca GPIO para manejo de los pines de la Raspberry PI
import time # Importa la biblioteca tiempo para la obtencion de fecha y hora

# Configuración de pines GPIO utilizando la numeracion de los GPIO
# Salida del servomotor de dirección
servo_pin = 18
servo_pin_cam = 9

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

# Pines del sensor ultrasónico HC-SR04 de la parte trasera
ultrasonico_trigger_2 = 20  # Pin TRIG del sensor
ultrasonico_echo_2 = 21     # Pin ECHO del sensor

# Pines del sensor ultrasónico HC-SR04 de la parte frontal
ultrasonico_trigger_1 = 16  # Pin TRIG del sensor
ultrasonico_echo_1 = 12     # Pin ECHO del sensor

def inicializar_componentes():
    # Configuracion de pines GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Configuracion de pines como salida
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setup(servo_pin_cam, GPIO.OUT)
    GPIO.setup(motor_del_izq_A, GPIO.OUT)
    GPIO.setup(motor_del_izq_B, GPIO.OUT)
    GPIO.setup(motor_del_der_A, GPIO.OUT)
    GPIO.setup(motor_del_der_B, GPIO.OUT)
    GPIO.setup(motor_tras_izq_A, GPIO.OUT)
    GPIO.setup(motor_tras_izq_B, GPIO.OUT)
    GPIO.setup(motor_tras_der_A, GPIO.OUT)
    GPIO.setup(motor_tras_der_B, GPIO.OUT)
    GPIO.setup(ultrasonico_trigger_1, GPIO.OUT)
    GPIO.setup(ultrasonico_echo_1, GPIO.IN)
    GPIO.setup(ultrasonico_trigger_2, GPIO.OUT)
    GPIO.setup(ultrasonico_echo_2, GPIO.IN)

    # Declarar las variables globales antes de usarlas
    global servo, servo_cam
    servo = GPIO.PWM(servo_pin, 50)
    servo_cam = GPIO.PWM(servo_pin_cam, 50)
    servo.start(7.5)
    servo_cam.start(7.5)

    global pwm_del_izqA, pwm_del_izqB, pwm_del_derA, pwm_del_derB
    global pwm_tras_izqA, pwm_tras_izqB, pwm_tras_derA, pwm_tras_derB
    
    pwm_del_izqA = GPIO.PWM(motor_del_izq_A, 100)
    pwm_del_izqB = GPIO.PWM(motor_del_izq_B, 100)
    pwm_del_derA = GPIO.PWM(motor_del_der_A, 100)
    pwm_del_derB = GPIO.PWM(motor_del_der_B, 100)
    pwm_tras_izqA = GPIO.PWM(motor_tras_izq_A, 100)
    pwm_tras_izqB = GPIO.PWM(motor_tras_izq_B, 100)
    pwm_tras_derA = GPIO.PWM(motor_tras_der_A, 100)
    pwm_tras_derB = GPIO.PWM(motor_tras_der_B, 100)
    
    for pwm in [pwm_del_izqA, pwm_del_izqB, pwm_del_derA, pwm_del_derB,
                pwm_tras_izqA, pwm_tras_izqB, pwm_tras_derA, pwm_tras_derB]:
        pwm.start(0)
    time.sleep(3)

def controlar_direccion_inv(error, error_anterior):
    Kp = 0.03  # Ganancia proporcional
    Kd = 0.01  # Ganancia derivativa

    parte_proporcional = Kp * error
    derivada_error = (error - error_anterior) / 0.1
    parte_derivativa = Kd * derivada_error

    correccion = parte_proporcional + parte_derivativa
    
    # Cambiar '-' a '+' para invertir el giro
    duty_cycle = max(5, min(10, 7.5 + correccion))
    servo.ChangeDutyCycle(duty_cycle)


# Controlador PD para la dirección
def controlar_direccion(error, error_anterior):
    Kp = 0.0008  # Ganancia proporcional
    Kd = 0.0004  # Ganancia derivativa

    parte_proporcional = Kp * error
    derivada_error = (error - error_anterior) / 0.1
    parte_derivativa = Kd * derivada_error

    correccion = parte_proporcional + parte_derivativa
    correccion = correccion * 0.6
    duty_cycle = max(5, min(10, 7.5 - correccion))
    servo.ChangeDutyCycle(duty_cycle)

def controlar_direccion1(error, error_anterior):
    Kp = 0.001  # Ganancia proporcional ajustada
    Kd = 0.0008  # Ganancia derivativa ajustada
    zona_muerta = 15
    # Si el error est� dentro de la zona muerta, no realizar ning�n ajuste
    if abs(error) < zona_muerta:
        return

    # Componentes del controlador PD
    parte_proporcional = Kp * error
    derivada_error = (error - error_anterior) / 0.25
    parte_derivativa = Kd * derivada_error

    # Correcci�n total
    correccion = parte_proporcional - parte_derivativa

    # Amortiguar los cambios bruscos
    correccion = correccion * 0.8  # Ajusta este factor para m�s suavidad

    # Calcular el ciclo de trabajo limitado
    duty_cycle = max(5, min(10, 7.5 + correccion))

    # Aplicar el cambio al servomotor
    servo.ChangeDutyCycle(duty_cycle)

def controlar_direccion2(error, error_anterior, area_detectada):
    Kp = 0.005  # Ganancia proporcional ajustada
    Kd = 0.0028  # Ganancia derivativa ajustada

    # Zona muerta din�mica: se incrementa conforme el �rea detectada aumenta
    zona_muerta = max(5, int(area_detectada / 6000))  # Ajuste el factor seg�n la sensibilidad deseada

    # Si el error est� dentro de la zona muerta, no realizar ning�n ajuste
    if abs(error) < zona_muerta:
        return

    # Componentes del controlador PD
    parte_proporcional = Kp * error
    derivada_error = (error - error_anterior) / 0.25
    parte_derivativa = Kd * derivada_error

    # Correcci�n total
    correccion = parte_proporcional - parte_derivativa

    # Amortiguar los cambios bruscos
    correccion = correccion * 0.8  # Ajusta este factor para m�s suavidad

    # Calcular el ciclo de trabajo limitado
    duty_cycle = max(3, min(12, 7.5 + correccion))

    # Aplicar el cambio al servomotor
    servo.ChangeDutyCycle(duty_cycle)

# Controlador PD suavizado para la direccion de la camara
def controlar_direccion_cam(error, error_anterior):
    Kp = 0.001  # Ganancia proporcional ajustada
    Kd = 0.0008  # Ganancia derivativa ajustada

    # Componentes del controlador PD
    parte_proporcional = Kp * error
    derivada_error = (error - error_anterior) / 0.25
    parte_derivativa = Kd * derivada_error

    # Correccion total
    correccion = parte_proporcional - parte_derivativa

    # Amortiguar los cambios bruscos
    correccion = correccion * 0.8  # Ajusta este factor para mas suavidad

    # Calcular el ciclo de trabajo limitado
    duty_cycle = max(5, min(10, 7.5 + correccion))

    # Aplicar el cambio al servomotor
    servo_cam.ChangeDutyCycle(duty_cycle)
    
def controlar_direccion_cam2(error, error_anterior, area_detectada):
    Kp = 0.001  # Ganancia proporcional ajustada
    Kd = 0.0008  # Ganancia derivativa ajustada

    # Zona muerta din�mica: se incrementa conforme el �rea detectada aumenta
    zona_muerta = max(5, int(area_detectada / 1000))  # Ajuste el factor seg�n la sensibilidad deseada

    # Si el error est� dentro de la zona muerta, no realizar ning�n ajuste
    if abs(error) < zona_muerta:
        return

    # Componentes del controlador PD
    parte_proporcional = Kp * error
    derivada_error = (error - error_anterior) / 0.25
    parte_derivativa = Kd * derivada_error

    # Correcci�n total
    correccion = parte_proporcional - parte_derivativa

    # Amortiguar los cambios bruscos
    correccion = correccion * 0.8  # Ajusta este factor para m�s suavidad

    # Calcular el ciclo de trabajo limitado
    duty_cycle = max(5, min(10, 7.5 + correccion))

    # Aplicar el cambio al servomotor
    servo_cam.ChangeDutyCycle(duty_cycle)

def controlar_direccion_cam1(error, error_anterior):
    Kp = 0.001  # Ganancia proporcional ajustada
    Kd = 0.0008  # Ganancia derivativa ajustada
    zona_muerta = 15
    # Si el error est� dentro de la zona muerta, no realizar ning�n ajuste
    if abs(error) < zona_muerta:
        return

    # Componentes del controlador PD
    parte_proporcional = Kp * error
    derivada_error = (error - error_anterior) / 0.25
    parte_derivativa = Kd * derivada_error

    # Correcci�n total
    correccion = parte_proporcional - parte_derivativa

    # Amortiguar los cambios bruscos
    correccion = correccion * 0.8  # Ajusta este factor para m�s suavidad

    # Calcular el ciclo de trabajo limitado
    duty_cycle = max(5, min(10, 7.5 + correccion))

    # Aplicar el cambio al servomotor
    servo_cam.ChangeDutyCycle(duty_cycle)

# Funcion para el control diferencial virtual
def ajustar_velocidades(error,velocidad_general):
     ajuste = error * 0.1  # Ajuste basado en el error

     # Calcular los ciclos de trabajo para cada rueda
     velocidad_izq = max(0, min(100, velocidad_general + ajuste))
     velocidad_der = max(0, min(100, velocidad_general - ajuste))

     # Establecer la dirección y velocidad de las ruedas traseras
     # Esta parte fue añadida para evitar inversion de giro de los motores
     if velocidad_izq > 0:
         pwm_tras_izqB.ChangeDutyCycle(0)  # Adelante
         pwm_tras_izqA.ChangeDutyCycle(velocidad_izq)
         pwm_del_izqB.ChangeDutyCycle(0)  # Adelante
         pwm_del_izqA.ChangeDutyCycle(velocidad_izq)
     else:
         pwm_tras_izqB.ChangeDutyCycle(velocidad_general)  # Reversa
         pwm_tras_izqA.ChangeDutyCycle(abs(velocidad_izq))
         pwm_del_izqB.ChangeDutyCycle(velocidad_general)  # Reversa
         pwm_del_izqA.ChangeDutyCycle(abs(velocidad_izq))

     if velocidad_der > 0:
         pwm_tras_derB.ChangeDutyCycle(0)  # Adelante
         pwm_tras_derA.ChangeDutyCycle(velocidad_der)
         pwm_del_derB.ChangeDutyCycle(0)  # Adelante
         pwm_del_derA.ChangeDutyCycle(velocidad_der)
     else:
         pwm_tras_derB.ChangeDutyCycle(velocidad_general)  # Reversa
         pwm_tras_derA.ChangeDutyCycle(abs(velocidad_der))
         pwm_del_derB.ChangeDutyCycle(velocidad_general)  # Reversa
         pwm_del_derA.ChangeDutyCycle(abs(velocidad_der))

# Control de los motores traseros
def controlar_motores(velocidad_general):
    # Motores traseros
    pwm_tras_izqB.ChangeDutyCycle(0)
    pwm_tras_derB.ChangeDutyCycle(0)
    # Ajustar PWM según la velocidad general
    pwm_tras_izqA.ChangeDutyCycle(velocidad_general)
    pwm_tras_derA.ChangeDutyCycle(velocidad_general)
    
    # Motores delanteros
    pwm_del_izqB.ChangeDutyCycle(0)
    pwm_del_derB.ChangeDutyCycle(0)
    # Ajustar PWM según la velocidad general
    pwm_del_izqA.ChangeDutyCycle(velocidad_general)
    pwm_del_derA.ChangeDutyCycle(velocidad_general)
        
# Detener el carro
def detener_carro():
    servo.ChangeDutyCycle(7.5) # Regresa la direccion a la posicion neutral
    pwm_del_izqA.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_del_derA.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_del_izqB.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_del_derB.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_tras_izqA.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_tras_derA.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_tras_izqB.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    pwm_tras_derB.ChangeDutyCycle(0) # Cambia el ciclo de trabajo a 0
    time.sleep(1)
    
# Detener el carro
def apaguar_carro():
    servo.ChangeDutyCycle(7.5) # Regresa la direccion a la posicion neutral
    servo_cam.ChangeDutyCycle(12) # Baja la articulacion de la camara
    pwm_del_izqA.stop() # Cambia el ciclo de trabajo a 0
    pwm_del_derA.stop() # Cambia el ciclo de trabajo a 0
    pwm_del_izqB.stop() # Cambia el ciclo de trabajo a 0
    pwm_del_derB.stop() # Cambia el ciclo de trabajo a 0
    pwm_tras_izqA.stop() # Cambia el ciclo de trabajo a 0
    pwm_tras_derA.stop() # Cambia el ciclo de trabajo a 0
    pwm_tras_izqB.stop() # Cambia el ciclo de trabajo a 0
    pwm_tras_derB.stop() # Cambia el ciclo de trabajo a 0
    time.sleep(3)
    servo.stop()
    servo_cam.stop()

# Función para dar vuelta hacia izquierda o derecha
def vuelta(sentido, velocidad, err):
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
        ajustar_velocidades(err, 5)  # Reducir velocidad en el lado izquierdo
        time.sleep(tiempo_giro)  # Tiempo de giro ajustado
    elif sentido.lower() == "derecha":
        # Calcular tiempo de giro ajustado a la velocidad
        tiempo_giro = tiempo_base_derecha * (20 / velocidad)
        print(f"Girando a la derecha con velocidad {velocidad}%... Tiempo de giro: {tiempo_giro:.2f} segundos")
        servo.ChangeDutyCycle(12)  # Posicion hacia la derecha
        ajustar_velocidades(err, 5)  # Reducir velocidad en el lado derecho
        time.sleep(tiempo_giro)  # Tiempo de giro ajustado
    else:
        print("Sentido invalido. Use 'izquierda' o 'derecha'.")
        return
    
    # Regresar a la posicion neutral y detener el ajuste de velocidades
    servo.ChangeDutyCycle(7.5)  # Regresar a la posicion neutral
    ajustar_velocidades(err, 0)  # Restablecer velocidades tras el giro

# Funcion de reversa
def reversa_carro(velocidad_general):
    # Ajustar motores traseros para reversa
    pwm_tras_izqA.ChangeDutyCycle(0)
    pwm_tras_derA.ChangeDutyCycle(0)
    pwm_tras_izqB.ChangeDutyCycle(velocidad_general)
    pwm_tras_derB.ChangeDutyCycle(velocidad_general)

    # Ajustar motores delanteros para reversa
    pwm_del_izqA.ChangeDutyCycle(0)
    pwm_del_derA.ChangeDutyCycle(0)
    pwm_del_izqB.ChangeDutyCycle(velocidad_general)
    pwm_del_derB.ChangeDutyCycle(velocidad_general)
    
# Funcion para finalizar el programa
def limpiar_gpio():
    apaguar_carro()
    GPIO.cleanup()
    
def stop_servo_cam():
    servo_cam.stop()

def CamDutyCycle(duty):
    servo_cam.ChangeDutyCycle(duty)

def DirDutyCycle(duty_cycle):
    servo.ChangeDutyCycle(duty_cycle)

import time

def smooth_servo_movement(servo_pwm, current_angle, target_angle, step=2, delay=0.05):
    """
    Mueve el servomotor de manera gradual desde el ángulo actual hasta el objetivo.
    :param servo_pwm: PWM del servomotor.
    :param current_angle: Ángulo actual del servomotor.
    :param target_angle: Ángulo deseado.
    :param step: Incremento en grados por paso.
    :param delay: Retardo entre cada paso (en segundos).
    """
    if current_angle < target_angle:
        angle_range = range(current_angle, target_angle + 1, step)
    else:
        angle_range = range(current_angle, target_angle - 1, -step)

    for angle in angle_range:
        duty_cycle = 2.5 + (angle / 18.0)  # Conversión de ángulo a ciclo de trabajo
        servo_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(delay)

    return target_angle  # Devuelve el nuevo ángulo actual
