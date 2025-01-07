import RPi.GPIO as GPIO
import time

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
    # Asegurar estado inicial bajo del TRIG
    GPIO.output(trigger, False)
    time.sleep(0.002)  # Esperar 2 ms para estabilización del sensor

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

    fin_pulso = time.time()
    while GPIO.input(echo) == 1:
        fin_pulso = time.time()
        if time.time() - inicio_pulso > 0.1:  # Evitar bucle infinito
            return float('inf')  # Retornar infinito si no se detecta respuesta

    # Calcular distancia
    duracion_pulso = fin_pulso - inicio_pulso
    distancia = duracion_pulso * 34300 / 2  # Velocidad del sonido: 34300 cm/s

    # Ignorar valores fuera de rango (por ejemplo, ruido)
    if distancia < 2 or distancia > 400:  # Rango típico de los sensores ultrasónicos
        return float('inf')  # Considerar fuera de rango

    return distancia

# Función para monitorear los sensores
def monitorear_sensores():
    try:
        # Leer distancias de ambos sensores
        distancia_frontal = medir_distancia(ultrasonico_trigger_1, ultrasonico_echo_1)
        time.sleep(0.1)  # Evitar interferencia entre sensores
        distancia_trasera = medir_distancia(ultrasonico_trigger_2, ultrasonico_echo_2)

        # Imprimir distancias
        print(f"Distancia Frontal: {distancia_frontal:.2f} cm | Distancia Trasera: {distancia_trasera:.2f} cm")

        # Verificar distancia mínima segura
        if distancia_frontal < 5:
            print("Obstáculo detectado en el frente, deteniendo vehículo")
            return True
        if distancia_trasera < 5:
            print("Obstáculo detectado atrás, deteniendo vehículo")
            return True
        elif distancia_frontal > 5 or distancia_trasera > 5:
            return False
    except Exception as e:
        print(f"Error al monitorear sensores: {e}")
        return False

# Limpieza de los pines GPIO al final del uso
def limpiar_gpio():
    GPIO.cleanup()

# Uso de prueba
if __name__ == "__main__":
    try:
        while True:
            if monitorear_sensores():
                print("Detenido por seguridad.")
            else:
                print("No se detectaron obstáculos cercanos.")
            time.sleep(0.5)  # Tiempo entre mediciones
    except KeyboardInterrupt:
        print("Saliendo del programa...")
    finally:
        limpiar_gpio()
