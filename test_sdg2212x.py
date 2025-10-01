#!/usr/bin/env python

"""
{ high-level module description }
"""
from instruments.instrument import Instrument
from instruments.function_generator import *
from time import sleep

import scipy.signal as sig
import matplotlib.pyplot as plt

def main():
    awg = connect_to_function_generator(
        model='SDG2122X'
    )
    awg.debug_enable = True
    awg.disable_output(channel=1)
    awg.disable_output(channel=2)
    awg.configure_channel(
        channel=1,
        polarity='nor',
        func='sine',
        amplitude=1.0,
        offset=1.0,
        frequency=2.25e3
    )
    awg.configure_channel(
        channel=2,
        polarity='nor',
        func='sine',
        amplitude=1.0,
        offset=1.0,
        frequency=2.75e3
    )
    awg.enable_output(channel=1)
    awg.enable_output(channel=2)
    ''' comine channel 1 and 2 to channel 1'''
    awg.enable_combine_channels(channel=1)

    awg.close()


if __name__ == '__main__':
    main()
