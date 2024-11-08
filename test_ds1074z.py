#!/usr/bin/env python

"""
test file for oscilloscope
"""
from instruments.instrument import Instrument
from instruments.oscilloscope import *
from time import sleep

import scipy.signal as sig
import matplotlib.pyplot as plt

def main():

    scope = connect_to_oscilloscope(
        model='DS1074Z'
    )
    scope.debug_enable = True
    scope.write_configs(
        configs=[
            'chan1:disp 1',
            'chan2:disp 0',
            'chan3:disp 0',
            'chan4:disp 0',

            'chan1:probe 1',
            'chan1:bwl 20M',
            'chan1:coup ac',
            'chan1:inv 0',
            'chan1:scal 1',
            'chan1:offset 0',

            'acq:norm',
            'acq:mdep 250000',

            'meas:clear all',
            'meas:sour chan1',

            'tim:mode main',
            'tim:scal 500e-6',

            'trig:mode edge',
            'trig:edge:slope pos',
            'trig:edge:source chan1',
            'trig:edge:level 500e-3',
            'trig:sweep auto',
            'run',
        ]
    )

    '''get some data'''
    sleep(2)

    ''' read out the freq measurement'''
    # scope.write('meas:item freq')
    print('channel 1 freq : ', scope.query('meas:item? freq'))

    ''' read out the peak to peak measurement '''
    # scope.write('meas:item vpp')
    print('channel 1 vpp  : ', scope.query('meas:item? vpp'))

    ''' read out the max period statistic of chan1 '''
    scope.write('meas:stat:item per')
    sleep(0.2)
    print('ch1 max period : ', scope.query('meas:stat:item? max,per'))

    '''capture traces of channel 1 from the screen'''
    wavs = []
    scope.write('trig:sweep single')
    scope.write('run')
    for _ in range(2):
        wavs.append(
            scope.get_waveform(ch=1, mode='norm')
        )
        scope.write('run')
    scope.write('stop')

    plt.figure()
    for w in wavs:
        plt.plot(w['time'], w['data'])
    plt.show()

    scope.close()

if __name__ == '__main__':
    main()
