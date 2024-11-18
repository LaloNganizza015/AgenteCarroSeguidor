from gpio_wrapper import GPIOController

# Inicializar el controlador GPIO
gpio = GPIOController()

# Pines
MOTOR_LEFT_FORWARD = 17
MOTOR_RIGHT_FORWARD = 27
STEERING_SERVO = 23

# Configuración inicial
gpio.setup_pin(MOTOR_LEFT_FORWARD, mode=gpio.GPIO.OUT)
gpio.setup_pin(MOTOR_RIGHT_FORWARD, mode=gpio.GPIO.OUT)
gpio.setup_pin(STEERING_SERVO, mode=gpio.GPIO.OUT)

# PWM
left_motor_pwm = gpio.create_pwm(MOTOR_LEFT_FORWARD, frequency=100)
right_motor_pwm = gpio.create_pwm(MOTOR_RIGHT_FORWARD, frequency=100)
steering_pwm = gpio.create_pwm(STEERING_SERVO, frequency=50)

gpio.start_pwm(MOTOR_LEFT_FORWARD, duty_cycle=0)
gpio.start_pwm(MOTOR_RIGHT_FORWARD, duty_cycle=0)
gpio.start_pwm(STEERING_SERVO, duty_cycle=7.5)  # Posición neutra

def move_forward(speed=50):
    gpio.set_pin_state(MOTOR_LEFT_FORWARD, state=gpio.GPIO.HIGH)
    gpio.set_pin_state(MOTOR_RIGHT_FORWARD, state=gpio.GPIO.HIGH)
    gpio.change_pwm_duty_cycle(MOTOR_LEFT_FORWARD, speed)
    gpio.change_pwm_duty_cycle(MOTOR_RIGHT_FORWARD, speed)

def stop_car():
    gpio.set_pin_state(MOTOR_LEFT_FORWARD, state=gpio.GPIO.LOW)
    gpio.set_pin_state(MOTOR_RIGHT_FORWARD, state=gpio.GPIO.LOW)
    gpio.change_pwm_duty_cycle(MOTOR_LEFT_FORWARD, 0)
    gpio.change_pwm_duty_cycle(MOTOR_RIGHT_FORWARD, 0)

def steer_with_rack_pinion(direction):
    if direction == "right":
        gpio.change_pwm_duty_cycle(STEERING_SERVO, 10.0)
    elif direction == "left":
        gpio.change_pwm_duty_cycle(STEERING_SERVO, 5.0)
    else:
        gpio.change_pwm_duty_cycle(STEERING_SERVO, 7.5)

def cleanup():
    gpio.cleanup()
