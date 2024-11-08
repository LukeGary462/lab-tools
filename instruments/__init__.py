from . import common
from . import instrument
from . import multimeter
from . import power_supply
from . import multi_function
from . import load
from . import oscilloscope
from . import function_generator
from . import spectrum_analyzer

import pprint as pp

def supported_instruments() -> dict:
    """
    get supported instruments
    """
    return {
        'multimeter': multimeter.MultimeterModels().models,
        'power_supply': power_supply.PowerSupplyModels().models,
        'multi_function': multi_function.MultiFunctionModels().models,
        'load': load.LoadModels().models,
        'oscilloscope': oscilloscope.OscilloscopeModels().models,
        'function_generator': function_generator.FunctionGeneratorModels().models,
    }

def connect_to_instrument(model: str, serial: str, **kwargs) -> object:
    """
    Connects to instrument.

    :param      model:   The model
    :type       model:   str
    :param      serial:  The serial
    :type       serial:  str
    :param      kwargs:  The keywords arguments
    :type       kwargs:  dictionary

    :returns:   connected instrument
    :rtype:     object
    """
    ''' look for the model in the supported list'''
    supported = supported_instruments()
    _cls = None
    inst_obj = None
    for k, v in supported.items():
        if model in v.keys():
            print(f'{model} is a {k}, attempting connection')
            _cls = v.get(model)
            break

    if _cls is None:
        raise Exception(
            f'{model} is not supported this intrument module version'
            f'\nsupported devices:\n'
            f'{pp.pformat(supported)}'
        )

    try:
        inst_obj = _cls(
            serial_number=serial,
            include_tcpip=kwargs.get('tcpip', False),
            include_rs232=kwargs.get('rs232', False)
        )
    except (VisaIOError, VisaIOWarning, InvalidSession):
        raise Exception(f'Could not connect to instrument {model}:{serial}')

    return inst_obj