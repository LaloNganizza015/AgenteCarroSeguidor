import RPi.GPIO as GPIO
import time
import motor_control as mc

# Pines del sensor ultrasónico HC-SR04 de la parte trasera
ultrasonico_trigger_2 = 20  # Pin TRIG del sensor
ultrasonico_echo_2 = 21     # Pin ECHO del sensor

# Pines del sensor ultrasónico HC-SR04 de la parte frontal
ultrasonico_trigger_1 = 16  # Pin TRIG del sensor
ultrasonico_echo_1 = 12     # Pin ECHO del sensor

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(ultrasonico_trigger_1, GPIO.OUT)
GPIO.setup(ultrasonico_echo_1, GPIO.IN)
GPIO.setup(ultrasonico_trigger_2, GPIO.OUT)
GPIO.setup(ultrasonico_echo_2, GPIO.IN)

# Función para medir la distancia de un sensor ultrasónico
def medir_distancia(trigger, echo):
    # Enviar pulso de activación
    GPIO.output(trigger, True)
    time.sleep(0.00001)  # Pulso de 10µs
    GPIO.output(trigger, False)

    # Medir el tiempo de ida y vuelta
    inicio_pulso = time.time()
    while GPIO.input(echo) == 0:
        inicio_pulso = time.time()
        if time.time() - inicio_pulso > 0.1:  # Evitar bucle infinito (timeout de 100ms)
            return float('inf')  # Retornar infinito si no se detecta respuesta

    while GPIO.input(echo) == 1:
        fin_pulso = time.time()
        if time.time() - inicio_pulso > 0.1:  # Evitar bucle infinito
            return float('inf')  # Retornar infinito si no se detecta respuesta

    # Calcular distancia
    duracion_pulso = fin_pulso - inicio_pulso
    distancia = duracion_pulso * 34300 / 2  # Velocidad del sonido: 34300 cm/s
    return distancia

# Función para monitorear los sensores
def monitorear_sensores():
    try:
        while True:
            # Leer distancias de ambos sensores
            distancia_frontal = medir_distancia(ultrasonico_trigger_1, ultrasonico_echo_1)
            time.sleep(0.1)  # Evitar interferencia entre sensores
            distancia_trasera = medir_distancia(ultrasonico_trigger_2, ultrasonico_echo_2)

            # Imprimir distancias
            print(f"Distancia Frontal: {distancia_frontal:.2f} cm | Distancia Trasera: {distancia_trasera:.2f} cm")

            # Verificar distancia mínima segura
            if distancia_frontal < 15:
                print("Obstáculo detectado en el frente, deteniendo vehículo")
                mc.detener_carro()

            if distancia_trasera < 15:
                print("Obstáculo detectado atrás, deteniendo vehículo")
                mc.detener_carro()

            time.sleep(0.5)  # Intervalo entre lecturas
    except KeyboardInterrupt:
        print("Finalizando monitoreo...")
    finally:
        GPIO.cleanup()

# Iniciar monitoreo
monitorear_sensores()
