#!/usr/bin/env python
# python 3
#pylint: disable=
##    @file:    test_dp832.py
#     @name:    Luke Gary
#  @company:    Honeywell
#     @date:    2025/10/1
################################################################################
# @copyright
#   Copyright 2025 Honeywell as an  unpublished work.
#   All Rights Reserved.
#
# @license The information contained herein is confidential
#   property of Honeywell. The user, copying, transfer or
#   disclosure of such information is prohibited except
#   by express written agreement with Honeywell.
################################################################################

"""
{ high-level module description }
"""
from instruments.instrument import Instrument
from instruments.power_supply import *
from time import sleep, time
import matplotlib.pyplot as plt


def main():
    psu = connect_to_power_supply(model='DP832')
    psu.debug_enable = True
    psu.write('syst:beep on')

    psu.set_output_voltage(3.3, 1)
    psu.set_output_current(20e-3, 1)

    psu.write('syst:beep:imm')
    psu.enable_source(1)
    sleep(1)
    psu.disable_source(1)

    psu.write('syst:beep off')
    psu.write('syst:local')
    psu.close()

if __name__ == '__main__':
    main()




