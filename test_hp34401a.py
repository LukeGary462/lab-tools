#!/usr/bin/env python

"""
{ high-level module description }
"""
from instruments.instrument import Instrument
from instruments.multimeter import *
from time import sleep, time
import matplotlib.pyplot as plt

def main():
    meter = connect_to_multimeter(model='34401A')
    meter.debug_enable = True
    meter.write_configs(
        configs=[
            # 'freq:aper 1'
        ]
    )

    sleep(1)
    resistances = []
    times = []
    for _ in range(100):
        v = meter.measure_resistance()
        print('resistance : ', v)
        resistances.append(v)
        # sleep(0.2)

    '''return to local mode'''
    meter.write('syst:local')

    plt.figure()
    plt.plot(resistances)
    plt.show()

    meter.close()

if __name__ == '__main__':
    main()
