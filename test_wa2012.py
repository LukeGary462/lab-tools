#!/usr/bin/env python
# python 3
#pylint: disable=
##    @file:    test_wa2012.py
#     @name:    Luke Gary
#  @company:    <company>
#     @date:    2025/9/10
################################################################################
# @copyright
#   Copyright 2025 <company> as an  unpublished work.
#   All Rights Reserved.
#
# @license The information contained herein is confidential
#   property of <company>. The user, copying, transfer or
#   disclosure of such information is prohibited except
#   by express written agreement with <company>.
################################################################################

"""
basic test script for remote control of Teledyne Lecroy WaveAce 2012 Oscilloscope
"""


from instruments.instrument import Instrument
from instruments.oscilloscope import *
from time import sleep

import scipy.signal as sig
import matplotlib.pyplot as plt

def main():
    print('RER instruments module, LGary 2019')
    print('Test Teledyle Lecroy WaveAce 2012 DSO')
    scope = connect_to_oscilloscope(
        model='WaveAce2012',
        scope_serial='LCRY2176C00701'
    )

    scope.default_setup()
    # trace_channel1 = scope.get_waveform(1)
    scope.write_configs(
        configs=[
            'trmd auto',
        ]
    )
    scope.close()


    # plt.figure()
    # plt.plot(trace_channel1.get('data'), label='channel 1')
    # plt.show()


if __name__ == '__main__':
    main()
