import RPi.GPIO as GPIO
import time

# Pines del sensor PIR
pir_pin = 16  # Cambia según la conexión física

# Pines del sensor ultrasónico HC-SR04
ultrasonico_trigger = 20  # Pin TRIG del sensor
ultrasonico_echo = 21     # Pin ECHO del sensor

# Pin del sensor de sonido (micrófono)
microfono_pin = 12  # Cambia según tu conexión

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_pin, GPIO.IN)
GPIO.setup(ultrasonico_trigger, GPIO.OUT)
GPIO.setup(ultrasonico_echo, GPIO.IN)
GPIO.setup(microfono_pin, GPIO.IN)

# Función para leer el sensor ultrasónico
def medir_distancia():
    # Enviar pulso de activación
    GPIO.output(ultrasonico_trigger, True)
    time.sleep(0.00001)  # Pulso de 10µs
    GPIO.output(ultrasonico_trigger, False)

    # Medir el tiempo de ida y vuelta
    while GPIO.input(ultrasonico_echo) == 0:
        inicio_pulso = time.time()
    while GPIO.input(ultrasonico_echo) == 1:
        fin_pulso = time.time()

    duracion_pulso = fin_pulso - inicio_pulso
    distancia = duracion_pulso * 34300 / 2  # Velocidad del sonido: 34300 cm/s

    return distancia

# Función para leer el sensor PIR
def detectar_movimiento():
    if GPIO.input(pir_pin):
        print("Movimiento detectado por PIR")
        detener_carro()  # Detener el vehículo
    else:
        print("No se detecta movimiento")

# Función para leer el sensor de sonido
def detectar_sonido():
    if GPIO.input(microfono_pin):
        print("Sonido fuerte detectado")
        detener_carro()  # Detener el vehículo
    else:
        print("Nivel de sonido normal")

# Función para monitorear los sensores
def monitorear_sensores():
    try:
        while True:
            # Leer datos de los sensores
            distancia = medir_distancia()
            print(f"Distancia medida: {distancia:.2f} cm")

            # Verificar distancia mínima segura
            if distancia < 30:  # Umbral de 30 cm
                print("Obstáculo detectado, deteniendo vehículo")
                detener_carro()
            
            # Leer el sensor PIR
            detectar_movimiento()

            # Leer el sensor de sonido
            detectar_sonido()

            time.sleep(0.5)  # Intervalo entre lecturas
    except KeyboardInterrupt:
        print("Finalizando monitoreo...")
    finally:
        GPIO.cleanup()

# Función para detener el vehículo
def detener_carro():
    pwm_del_izq.ChangeDutyCycle(0)
    pwm_del_der.ChangeDutyCycle(0)
    pwm_tras_izq.ChangeDutyCycle(0)
    pwm_tras_der.ChangeDutyCycle(0)
    servo.ChangeDutyCycle(7.5)  # Posición neutral para el servo
    print("Vehículo detenido")

# Iniciar monitoreo
monitorear_sensores()
