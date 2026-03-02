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
    def successive_approximation_adc(self):
        vr=255
        vl=0
        k=[int(bit) for bit in bin(int(vl))[2:].zfill(8)]
        GPIO.output(self.bits_gpio , k)
        time.sleep(1)
        while vl < vr-0.1:
            v=(vl+vr)/2
            time.sleep(0.1)
            k=[int(bit) for bit in bin(int(v))[2:].zfill(8)]
            GPIO.output(self.bits_gpio , k)
            if not GPIO.input(self.comp_gpio):
                vl=v
            else:
                vr=v
        
        return vr
    def get_sar_voltage(self):
        print(self.successive_approximation_adc(), '================================')
    def deinit(self):
        GPIO.output(self.bits_gpio , 0)
        GPIO.cleanup()
        
try:
    dac = R2R_ADC(3.2, True)
    while True:
        try:
            dac.get_sar_voltage()
            time.sleep(3)
        except ValueError:
            print("Вы ввели не число. Попробуйте ещё раз\n")

finally:
    dac.deinit()