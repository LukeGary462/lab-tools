#!/usr/bin/env python

"""
DC Loads
"""


from instruments.instrument import Instrument
from pyvisa import (VisaIOError, VisaIOWarning, InvalidSession)

class LoadModels:
    """
    This class describes dc load models.
    """
    def __init__(self):
        self.models = {}
        self.models['DL3021'] = DL3021

    def get(self, model: str) -> Instrument:
        """
        Gets the specified model.

        :param      model:  The model
        :type       model:  str

        :returns:   dc load object
        :rtype:     Instrument
        """
        return self.models.get(model, None)

    def is_valid(self, model: str) -> bool:
        """
        Determines whether the specified model is valid.

        :param      model:  The model
        :type       model:  str

        :returns:   True if the specified model is valid, False otherwise.
        :rtype:     bool
        """
        return model in self.models.keys()

def connect_to_load(model: str, dc_load_serial: str = None, tcpip: bool = False, rs232: bool = False) -> object:
    """
    Connects to dc load based on a model string.

    :param      model:         The model
    :type       model:         str
    :param      dc_load_serial:  The meter serial
    :type       dc_load_serial:  str

    :returns:   multimeter object if model is valid, None if not
    :rtype:     object
    """
    dc_load_obj = None
    dc_load = DCLoadModels().get(model)
    if dc_load:
        try:
            dc_load_obj = dc_load(
                serial_number=dc_load_serial,
                include_tcpip=tcpip,
                include_rs232=rs232,
                )
        except (VisaIOError, VisaIOWarning, InvalidSession):
            print(f'Could not connect to a dc load with model:serial {model}:{dc_load_serial}')
            dc_load_obj = None
    return dc_load_obj

class DL3021(Instrument):
    """
    This class describes a rigol dl3021 dc load.
    https://www.batronix.com/files/Rigol/Elektronische-Lasten/DL3000/DL3000_ProgrammingManual_EN.pdf
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='DL3021', **kwargs)

    def measure_voltage(self):
        """
        measure load voltage, autoranging by default
        """
        res = self.query(f'meas:volt?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_current(self):
        """
        measure load current, autoranging by default
        """
        res = self.query(f'meas:curr?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_power(self):
        """
        measure load power, autoranging by default
        """
        res = self.query(f'meas:pow?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def measure_resistance(self):
        """
        measure load resistance, autoranging by default
        """
        res = self.query('meas:res?')
        if res is not None:
            return float(res)
        self.debug(f'Measurement Error')
        return res

    def set_cc_slew_rate(self, slew):
        # My DL3021 returns a string like '0.000067\n0'
        self.write(f":SOURCE:CURRENT:SLEW {slew}")

    def is_enabled(self):
        """
        Enable the electronic load
        Equivalent to pressing "ON/OFF" when the load is ON
        """
        return self.query(":SOURCE:INPUT:STAT?").strip() == "1"

    def enable(self):
        """
        Enable the electronic load
        Equivalent to pressing "ON/OFF" when the load is ON
        """
        self.write(":SOURCE:INPUT:STAT ON")

    def disable(self):
        """
        Disable the electronic load
        Equivalent to pressing "ON/OFF" when the load is ON
        """
        self.write(":SOURCE:INPUT:STAT OFF")

    def set_mode(self, mode="CC"):
        """
        Set the load mode to "CURRENT", "VOLTAGE", "RESISTANCE", "POWER"
        """
        self.write(":SOURCE:FUNCTION {}".format(mode))

    def query_mode(self):
        """
        Get the mode:
        "CC", "CV", "CR", "CP"
        """
        return self.query(":SOURCE:FUNCTION?").strip()

    def set_cr_resistance(self, resistance):
        """
        sets CR resistance value in Ohms
        """
        return self.write(":SOURCE:RES:LEV:IMM {}".format(resistance))

    def set_cc_current(self, current):
        """
        Set CC current limit
        """
        return self.write(":SOURCE:CURRENT:LEV:IMM {}".format(current))

    def set_cp_power(self, power):
        """
        Set CP power limit
        """
        return self.write(":SOURCE:POWER:LEV:IMM {}".format(power))

    def set_cp_ilim(self, ilim):
        """
        Set CP current limit
        """
        return self.query(":SOURCE:POWER:ILIM {}".format(ilim))

    def cc(self, current, activate=True):
        """
        One-line constant-current configuration.
        if activate == True, also turns on the power supply
        """
        self.set_mode("CC")
        self.set_cc_current(current)
        self.enable()

    def cp(self, power, activate=True):
        """
        One-line constant-current configuration.
        if activate == True, also turns on the power supply
        """
        self.set_mode("CP")
        self.set_cp_power(power)
        self.enable()

    def cr(self, resistance, activate=True):
        """
        one-line constant resistance config

        :param      resistance:  The resistance
        :type       resistance:  float
        :param      activate:    The activate
        :type       activate:    bool
        """
        self.set_mode('CR')
        self.set_cr_resistance(resistance)
        self.enable()

