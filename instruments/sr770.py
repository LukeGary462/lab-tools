#!/usr/bin/env python

"""
VISA interface to Stanford Research Systems SR770 Dynamic Signal Analyzer
"""
from typing import Dict
try:
    from instruments.instrument import Instrument
except ModuleNotFoundError:
    from instrument import Instrument
from pyvisa import (VisaIOError, VisaIOWarning, InvalidSession)

import numpy as np

SPAN = {
    '191 mHz': 0,
    '382 mHz': 1,
    '763 mHz': 2,
    '1.5 Hz': 3,
    '3.1 Hz': 4,
    '6.1 Hz': 5,
    '12.2 Hz': 6,
    '24.4 Hz': 7,
    '48.75 Hz': 8,
    '97.5 Hz': 9,
    '195 Hz': 10,
    '390 Hz': 11,
    '780 Hz': 12,
    '1.56 kHz': 13,
    '3.125 kHz': 14,
    '6.25 kHz': 15,
    '12.5 kHz': 16,
    '25 kHz': 17,
    '50 kHz': 18,
    '100 kHz': 19,
}

class SR770(Instrument):
    """
    This class describes a sr770 dynamic signal analyzer.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='SR770', **kwargs)

        # initialize instrument
        response = self.write('OUTP 0')


    def measure_psd_full_span(self) -> Dict:
        """
        measure the full span of the instrument

        :param      span:  The span identifier, 19 = full span
        :type       span:  int

        :returns:   Dict of {Freq(Hz), PSD (Vrms/rt-Hz)}
        :rtype:     Dict
        """
        # check this ...
        freq_array = np.linspace(250, 100000, 400, dtype=float)

        # full span measurement from ~0Hz to 104kHz
        response = self.write('span 19')
        # set to PSD measurement
        response = self.write('meas -1, 1')
        # move trace marker to bin i=0
        response = self.write('mbin -1, 0')

        self.device.read_termination = '\r'
        self.device.timeout = 25000

        psd_raw = self.query('spec? -1')
        psd_raw = psd_raw.split(',')

        psd_volts_rt_hz = []
        for psd in psd_raw:
            if psd:
                try:
                    psd_volts_rt_hz.append(float(psd))
                except ValueError:
                    print(f'Could not cast {psd} to float')

        # psd_full = np.vstack((freq_array))

        return {
            'psd': psd_volts_rt_hz,
            'freqs': freq_array
        }

def test():
    ''' test the API'''
    dsa = SR770(debug=True)
    import pprint as pp
    import matplotlib.pyplot as plt
    pp.pprint(dsa.query('*idn?'))
    PSD = dsa.measure_psd_full_span()
    plt.figure()
    plt.semilogx(PSD.get('freqs'), PSD.get('psd'))
    plt.show()


if __name__ == '__main__':
    test()
