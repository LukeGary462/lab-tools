#!/usr/bin/env python

from instruments.instrument import Instrument
from instruments.common import (get_numbers_from_line)
from pyvisa import (InvalidSession)

class ThermalProbes(Instrument):
    """
    This class describes custom thermal probes.
    """
    '''tentative'''
    models = [
        'HeatCalRevB',
        'ProbeHatRevA'
    ]

    def __init__(self, **kwargs):
        """
        constructor
        """
        super().__init__(**kwargs)
        kwargs['include_rs232'] = True
        kwargs['include_tcpip'] = False
        self.__inst_init__(model='HeatCalRevB', **kwargs)


    def get_probe_temp(self, probe_idx: int = 0) -> Dict:
        """
        Gets the probe temporary.
        
        :param      probe_idx:  The probe index
        :type       probe_idx:  int
        """
        if probe_idx not in range(0, 9):
            self.debug(f'{probe_idx} is an invalid temp probe index')
            return None

        res = self.query(f'meas:probe? {probe_idx}')
        ret = {
            'time': None,
            'temp': None,
            'probe': probe_idx
        }
        if res:
            nums = get_numbers_from_line(res)
            if len(nums) == 2:
                ret['time'] = nums[1]
                ret['temp'] = nums[0]
        return ret
