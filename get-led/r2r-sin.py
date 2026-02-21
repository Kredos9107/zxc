import r2r_dac as r2r
import signal_gen as sg
import time

amplitude = 3
signal_frequency = 10
sampling_frequency = 1000
t=0

try:
    dac = r2r.R2R_DAC([16,20,21,25,26,17,27,22], 3.183, True)
    while True:
        d=sg.get_sin_wave_amplitude(signal_frequency, t)*amplitude
        print(d)
        dac.set_voltage(d)
        sg.wait_for_sampling_period(sampling_frequency)
        t+=1/sampling_frequency
finally:
    dac.deinit()