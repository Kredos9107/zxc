import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
leds = [16, 12, 25, 17, 27, 23, 22, 24]
GPIO.setup(leds, GPIO.OUT)
GPIO.setup(9, GPIO.IN)
GPIO.setup(10, GPIO.IN)
num=0
def dec2bin(value):
    return [int(element) for element in bin(value)[2:].zfill(8)]
sleep_time = 0.2
while True:
    if GPIO.input(9):
        time.sleep(sleep_time)
        num = num + 1
        print(num, dec2bin(num))
    if GPIO.input(10):
        time.sleep(sleep_time)
        num = num - 1
        print(num, dec2bin(num))
    GPIO.output(leds, dec2bin(num))
    if GPIO.input(9) and GPIO.input(10):
        num=254