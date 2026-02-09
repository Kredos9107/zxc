import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
led=26
phot=6
state=0
GPIO.setup(led, GPIO.OUT)
GPIO.setup(phot, GPIO.IN)

while True:
    GPIO.output(led, not GPIO.input(phot))
    time.sleep(0.2)
    