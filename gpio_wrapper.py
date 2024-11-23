#import RPi.#GPIO as #GPIO

class #GPIOController:
    def __init__(self):
        # Configuración inicial del modo #GPIO
        ##GPIO.setmode(#GPIO.BCM)
        self.pwm_channels = {}  # Para almacenar los canales PWM creados

    def setup_pin(self, pin, mode, initial=None):
        """
        Configura un pin #GPIO en un modo específico.
        :param pin: Número del pin #GPIO.
        :param mode: #GPIO.OUT o #GPIO.IN.
        :param initial: Estado inicial si el modo es OUTPUT (#GPIO.HIGH o #GPIO.LOW).
        """
        if mode == #GPIO.OUT and initial is not None:
            #GPIO.setup(pin, mode, initial=initial)
        else:
            #GPIO.setup(pin, mode)

    def set_pin_state(self, pin, state):
        """
        Cambia el estado de un pin #GPIO.
        :param pin: Número del pin #GPIO.
        :param state: #GPIO.HIGH o #GPIO.LOW.
        """
        #GPIO.output(pin, state)

    def create_pwm(self, pin, frequency):
        """
        Crea un canal PWM en un pin #GPIO.
        :param pin: Número del pin #GPIO.
        :param frequency: Frecuencia en Hz.
        :return: Objeto PWM.
        """
        pwm = #GPIO.PWM(pin, frequency)
        self.pwm_channels[pin] = pwm
        return pwm

    def start_pwm(self, pin, duty_cycle):
        """
        Inicia PWM en un pin con un ciclo de trabajo.
        :param pin: Número del pin #GPIO.
        :param duty_cycle: Ciclo de trabajo inicial (0-100%).
        """
        if pin in self.pwm_channels:
            self.pwm_channels[pin].start(duty_cycle)
        else:
            raise ValueError(f"No se ha configurado PWM en el pin {pin}")

    def change_pwm_duty_cycle(self, pin, duty_cycle):
        """
        Cambia el ciclo de trabajo de un canal PWM.
        :param pin: Número del pin #GPIO.
        :param duty_cycle: Nuevo ciclo de trabajo (0-100%).
        """
        if pin in self.pwm_channels:
            self.pwm_channels[pin].ChangeDutyCycle(duty_cycle)
        else:
            raise ValueError(f"No se ha configurado PWM en el pin {pin}")

    def stop_pwm(self, pin):
        """
        Detiene el canal PWM en un pin.
        :param pin: Número del pin #GPIO.
        """
        if pin in self.pwm_channels:
            self.pwm_channels[pin].stop()
            del self.pwm_channels[pin]
        else:
            raise ValueError(f"No se ha configurado PWM en el pin {pin}")

    def cleanup(self):
        """
        Limpia todos los pines #GPIO configurados.
        """
        #GPIO.cleanup()
