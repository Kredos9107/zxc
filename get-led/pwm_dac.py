import RPi.GPIO as GPIO
import time

class PWM_DAC:
    def __init__(self, gpio_pin, pwm_frequency, dynamic_range, verbose = False):
        self.gpio_pin = gpio_pin
        self.pwm_frequency = pwm_frequency
        self.dynamic_range = dynamic_range
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.gpio_pin, self.pwm_frequency)
    def set_number(self, number):
        self.pwm.start(number)
    def set_voltage(self, voltage):
        voltage = voltage / self.dynamic_range*100
        print(voltage)
        self.set_number(voltage)
    def deinit(self):
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.gpio_pin, 0)
        GPIO.cleanup()


if __name__ == "__main__":
    try:
        dac = PWM_DAC(12, 1000, 3.28, True)
        
        while True:
            try:
                voltage = float(input("Введите напряжение в Вольтах: "))
                dac.set_voltage(voltage)

            except ValueError:
                print("Вы ввели не число. Попробуйте ещё раз\n")
    finally:
        dac.deinit()