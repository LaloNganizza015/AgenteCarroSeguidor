import RPi.GPIO as GPIO  # Importa la biblioteca GPIO para manejo de los pines de la Raspberry Pi
import time  # Importa la biblioteca tiempo para la obtención de fecha y hora
import motor_control as mc  # Importa el módulo de control de los motores

# Parámetro de velocidad general
velocidad_general = 20

# Función para avanzar durante 2 segundos
def avanzar2seg(vel):
    print("Avanzando durante 2 segundos...")
    mc.controlar_motores(vel)
    time.sleep(2)  # Avanza durante 2 segundos
    mc.detener_carro()  # Detiene el carro al finalizar

# Función para avanzar durante 1 segundo
def avanzar1seg(vel):
    print("Avanzando durante 1 segundo...")
    mc.controlar_motores(vel)
    time.sleep(1)  # Avanza durante 1 segundo
    mc.detener_carro()  # Detiene el carro al finalizar

# Función de predicción para ejecutar acciones basadas en la entrada
def prediccion(accion, vel, err):
    try:
        # Inicializar componentes si es necesario
        # mc.inicializar_componentes()

        # Diccionario de acciones
        acciones = {
            'adelante': avanzar2seg(vel),
            'derecha': lambda: mc.vuelta('derecha', vel, err),
            'izquierda': lambda: mc.vuelta('izquierda', vel, err),
            'alto': mc.detener_carro(),
            'reversa': lambda: (mc.reversa_carro(vel), time.sleep(1), mc.detener_carro())
        }

        # Ejecutar la acción correspondiente
        if accion in acciones:
            acciones[accion]()  # Llama a la función correspondiente
        else:
            print(f"Acción desconocida: {accion}. Deteniendo por seguridad.")
            mc.detener_carro()  # Comportamiento por defecto para acciones no válidas

    except Exception as e:
        print(f"Error al ejecutar la predicción: {e}")
        mc.detener_carro()  # Asegura detener el carro en caso de error
