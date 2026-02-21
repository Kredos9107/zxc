import mcp4725_driver as mc
import signal_gen as sg
import time

amplitude = 3
signal_frequency = 10
sampling_frequency = 100
t=0

try:
    m=mc.MCP4725(5, True)
    while True:
        d=sg.get_sin_wave_amplitude(signal_frequency, t)*amplitude
        print(d)
        m.set_voltage(d)
        sg.wait_for_sampling_period(sampling_frequency)
        t+=1/sampling_frequency
finally:
    m.deinit()