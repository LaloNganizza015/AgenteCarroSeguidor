import cv2
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
import os

servo_pin_cam = 9

duty_cycle=7.5

GPIO.setmode(GPIO.BCM)

GPIO.setup(servo_pin_cam, GPIO.OUT)

servo = GPIO.PWM(servo_pin_cam, 50)

servo.start(duty_cycle)

# Configuración inicial
output_folder = "capturas"
os.makedirs(output_folder, exist_ok=True)  # Crear la carpeta si no existe
camera = Picamera2()


# Configurar la resolución de la cámara
camera_config = camera.create_preview_configuration({"size": (64, 64)})
camera.configure(camera_config)

# Iniciar la cámara
camera.start()

print("Presiona 's' para capturar una imagen. Presiona 'q' para salir.")

try:
    while True:
        # Capturar fotogramas en tiempo real
        frame = camera.capture_array()
        
        # Mostrar el video en una ventana
        cv2.imshow("Video en tiempo real", frame)



        # Leer una tecla presionada
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):  # Si se presiona 's', tomar una foto
            filename = os.path.join(output_folder, f"foto_{len(os.listdir(output_folder)) + 1}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Foto guardada en {filename}")
        
        elif key == ord('q'):  # Salir si se presiona 'q'
            break
            
        if key == ord('e'):
            duty_cycle = duty_cycle + 0.5
        elif key == ord('r'):
            duty_cycle = duty_cycle - 0.5
        servo.ChangeDutyCycle(duty_cycle)

finally:
    # Liberar recursos
    camera.stop()
    cv2.destroyAllWindows()
    print("Programa finalizado.")
