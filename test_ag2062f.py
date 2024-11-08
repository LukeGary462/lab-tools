#!/usr/bin/env python

"""
test owon AG2062F arbitrary waveform generator
"""
from instruments.instrument import Instrument
from instruments.function_generator import *
from time import sleep

import scipy.signal as sig
import matplotlib.pyplot as plt

def main():
    # awg = connect_to_function_generator(
        # model='AG2062F'
    # )
    # awg.debug_enable = True
    A = np.asarray([1,0.5,0.25,0,-.25,-.5,-1,-.5,-.25,0,.25,.5])
    print(AG2062F.create_arbitrary_waveform_file(data=A, filename='test.bin'))
    print(AG2062F.create_arbitrary_waveform_file(data=A, filename='test.bin', resample=True, numpts=50))

if __name__ == '__main__':
    main()
