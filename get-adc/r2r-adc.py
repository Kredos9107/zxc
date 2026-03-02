import RPi.GPIO as GPIO
import time
class R2R_ADC:
    def __init__(self, dynamic_range, compare_time = 0.007, verbose = False):
        self.dynamic_range = dynamic_range
        self.verbose = verbose
        self.compare_time = compare_time
        
        self.bits_gpio = [26, 20, 19, 16, 13, 12, 25, 11]
        self.comp_gpio = 21

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.bits_gpio, GPIO.OUT, initial = 0)
        GPIO.setup(self.comp_gpio, GPIO.IN)
        
    def sequential_counting_adc(self):
        v=0
        while True:
            if not GPIO.input(self.comp_gpio):
                print(v,GPIO.input(self.comp_gpio))
                v+=1
                k=[int(bit) for bit in bin(v)[2:].zfill(8)]
                GPIO.output(self.bits_gpio , k)
            else:
                print(v,GPIO.input(self.comp_gpio))
                v-=1
                k=[int(bit) for bit in bin(v)[2:].zfill(8)]
                GPIO.output(self.bits_gpio , k)
            time.sleep(0.005)
    def deinit(self):
        GPIO.output(self.bits_gpio , 0)
        GPIO.cleanup()
        
try:
    dac = R2R_ADC(3.2, True)
    while True:
        try:
            dac.sequential_counting_adc()
        except ValueError:
            print("Вы ввели не число. Попробуйте ещё раз\n")

finally:
    dac.deinit()