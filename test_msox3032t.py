#!/usr/bin/env python

"""
test file for mso-x 3032T oscilloscope
"""
from instruments.instrument import Instrument
from instruments.oscilloscope import *
from time import sleep

import scipy.signal as sig
import scipy.fft as fft
import matplotlib.pyplot as plt

def main():
    scope = connect_to_oscilloscope(
        model='MSOX3032T'
    )
    scope.debug_enable = True
    scope.write_configs(
        configs=[
            'chan1:disp 1',
            'chan2:disp 0',
            'chan1:bwl 1',
            'chan1:coup ac',
            'chan1:inv 0',
            'chan1:scal 1000mV',
            'tim:mode main',
            'trig:mode edge',
            'trig:level 950mV 1',
        ]
    )

    '''capture traces of channel 1 from the screen'''
    def capture_test():
        wavs = []
        for _ in range(2):
            wavs.append(
                scope.get_digitized_waveform(
                    ch=1,
                    sample_rate=1.5e6,
                    sample_duration=50e-3,
                    force_trigger=True
                )
            )

        scope.write('stop')

        ''' do some filtering '''
        plt.figure()
        filtered = []
        for idx, w in enumerate(wavs):
            plt.plot(w['time'], w['data'], label=f'capture-{idx}, raw')
            b, a = sig.bessel(2, 0.25)
            y = sig.filtfilt(b, a, w['data'], padlen=10)
            w['filt'] = y
            filtered.append(w)
            plt.plot(w['time'], y, label=f'capture-{idx}, filt')


        '''calculate the fft of the first filtered trace'''
        timestep = filtered[0]['preamble']['xinc']
        numsamples = len(filtered[0]['filt'])
        w = sig.hann(numsamples)
        # plt.plot(filtered[0]['time'], filtered[0]['filt']*w, label='cap-0-windowed')
        plt.legend(loc='best')

        yf = fft.fft(filtered[0]['data']*w)
        xf = fft.fftfreq(numsamples, timestep)[:numsamples//2]
        plt.figure()
        plt.loglog(xf, 2.0/numsamples*np.abs(yf[0:numsamples//2]))
        plt.grid()
        plt.show()

    def sample_rate_test():
        pass

    capture_test()
    scope.close()

if __name__ == '__main__':
    main()
