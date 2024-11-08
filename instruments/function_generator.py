#!/usr/bin/env python

"""
function and arbitrary waveform generators
"""
import numpy as np
from scipy import signal
from instruments.instrument import Instrument
from pyvisa import (VisaIOError, InvalidSession, VisaIOWarning)
from datetime import datetime
from os import remove

class FunctionGeneratorModels:
    """
    This class describes function generator models.
    """
    def __init__(self):
        self.models = {}
        ''' AG2062F driver installation process is extremely complex
            to get it to respond over standard IVI/VISA...
            disabling this class for now
        '''
        # self.models['AG2062F'] = AG2062F
        self.models['SDG2122X'] = SDG2122X

    def get(self, model: str) -> Instrument:
        """
        Gets the specified model.

        :param      model:  The model
        :type       model:  str

        :returns:   FuncGen class
        :rtype:     Instrument
        """
        return self.models.get(model, None)

    def is_valid(self, model: str) -> bool:
        return model in self.models.keys()

def connect_to_function_generator(
    model: str,
    funcgen_serial: str = None,
    rs232: bool = False,
    tcpip: bool = False) -> object:
    """
    Connects to funcgen.

    :param      model:         The model
    :type       model:         str
    :param      funcgen_serial:  The funcgen serial number
    :type       funcgen_serial:  str
    :param      tcpip:         The tcpip
    :type       tcpip:         bool

    :returns:   funcgen obbject if model is valid, none if not
    :rtype:     object
    """
    funcgen_obj = None
    funcgen = FunctionGeneratorModels().get(model)
    if funcgen:
        try:
            funcgen_obj = funcgen(
                serial_number=funcgen_serial,
                include_tcpip=tcpip,
                include_rs232=rs232,
                )
        except (VisaIOError, VisaIOWarning, InvalidSession):
            raise Exception(f'Could not connect to funcgen {model}:{funcgen_serial}')
    return funcgen_obj

class SDG2122X(Instrument):
    """
    This class describes a sdg 2122 x.
    https://siglentna.com/USA_website_2014/Documents/Program_Material/SDG_ProgrammingGuide_PG_E03B.pdf
    """
    built_in_arb = {
        'Sine':     0, 'Logfall':   12, 'Gmonopuls': 24, 'Triang':   36,
        'Noise':    1, 'Logrise':   13, 'Tripuls':   25, 'Harris':   37,
        'StairUp':  2, 'Sqrt':      14, 'Cardiac':   26, 'Bartlett': 38,
        'StairDn':  3, 'Root3':     15, 'Quake':     27, 'Tan':      39,
        'Stairud':  4, 'X^2':       16, 'Chirp':     28, 'Cot':      40,
        'Ppulse':   5, 'X^3':       17, 'Twotone':   29, 'Sec':      41,
        'Npulse':   6, 'Sinc':      18, 'Snr':       30, 'Csc':      42,
        'Trapezia': 7, 'Gaussian':  19, 'Hamming':   31, 'Asin':     43,
        'Upramp':   8, 'Dlorentz':  20, 'Hanning':   32, 'Acos':     44,
        'Dnramp':   9, 'Haversine': 21, 'Kaiser':    33, 'Atan':     45,
        'Exp_fall': 1, 'Lorentz':   22, 'Blackman':  34, 'Acot':     46,
        'Exp_rise': 1, 'Gauspuls':  23, 'Gausswin':  35, 'Squar':    47,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='SDG2122X', **kwargs)
        self.write('buzz on')

    def enable_output(self, **kwargs):
        """
        Enables the output.

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ch = int(kwargs.get('channel', 1))
        self.write(f'c{ch}:outp on')

    def disable_output(self, **kwargs):
        """
        Disables the output.

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ch = int(kwargs.get('channel', 1))
        self.write(f'c{ch}:outp off')

    def configure_channel(self, **kwargs):
        """
        configure a channel

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ch       = int(kwargs.get('channel', 1))
        ch = ch if (ch<=2 and ch>0) else 1

        ''' format polarity'''
        polarity = kwargs.get('polarity', 'nor')
        polarity = polarity if polarity.lower() in ['nor', 'invt'] else 'nor'

        ''' format load, implicit dtype change to str'''
        load     = float(kwargs.get('load', 2e5))
        load = load if load < 1e5 and load > 50 else 'HZ'
        ''' config output '''
        self.write_configs(
            configs=[
                f'c{ch}:outp load,{load}',
                f'c{ch}:outp plrt,{polarity}'
            ]
        )

        freq     = float(kwargs.get('frequency', 1e3))
        period   = float(kwargs.get('period', 0))
        phase    = float(kwargs.get('phase', 0))
        ampl     = float(kwargs.get('amplitude', 1.0))
        offs     = float(kwargs.get('offset', 0.0))
        outRange = kwargs.get('range', [0])
        func     = kwargs.get('function', 'sine')

        valid_functions = ['sine', 'square', 'ramp', 'pulse', 'noise', 'arb', 'dc', 'prbs']
        if func not in valid_functions:
            raise Exception(f'{func} not supported.\nvalid funcs: {valid_functions}')
        self.write_configs(
            configs=[
                f'c{ch}:bswv wvtp,{func}',
                f'c{ch}:bswv frq,{freq}',
                f'c{ch}:bswv phse,{phase}',
            ]
        )

        ''' set output voltage '''
        if len(outRange) == 2:
            self.write_configs(
                configs=[
                    f'c{ch}:bswv hlev,{outRange[-1]}',
                    f'c{ch}:bswv llev,{outRange[0]}',
                ]
            )
        else:
            self.write_configs(
                configs=[
                    f'c{ch}:bswv amp,{ampl}',
                    f'c{ch}:bswv ofst,{offs}',
                ]
            )


    def enable_combine_channels(self, **kwargs):
        """
        combine output channels

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ch       = int(kwargs.get('channel', 1))
        ch = ch if (ch<=2 and ch>0) else 1
        self.write(f'c{ch}:cmbn on')

    def disable_combine_channels(self, **kwargs):
        """
        combine output channels

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ch       = int(kwargs.get('channel', 1))
        ch = ch if (ch<=2 and ch>0) else 1
        self.write(f'c{ch}:cmbn off')


class AG2062F(Instrument):
    """
    This class describes an OWON ag2062f arbitrary waveform generator.
    """
    ''' built in waveforms (appendix b) '''
    built_in_arb = {
        'StairD': 0,
        'StairU': 1,
        'StairUD': 2,
        'Trapezia': 3,
        'RoundHalf': 4,
        'AbsSine': 5,
        'AbsSineHalf': 6,
        'SineTra': 7,
        'SineVer': 8,
        'ExpRise': 9,
        'ExpFall': 10,
        'Sinc': 11,
        'Tan': 12,
        'Cot': 13,
        'Sqrt': 14,
        'x^2': 15,
        'Rectangle': 16,
        'Gauss': 17,
        'Hamming': 18,
        'Hann': 19,
        'Bartlett': 20,
        'Blackman': 21,
        'Laylight': 22,
        'DC': 23,
        'Heart': 24,
        'Round': 25,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='AG2062F', **kwargs)

    def enable_output(self, **kwargs):
        """
        Enables the output.

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ch = kwargs.get('channel', 'ch1')
        self.write(f'chan:{ch} on')

    def disable_output(self, **kwargs):
        """
        Disables the output.

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ch = kwargs.get('channel', 'ch1')
        self.write(f'chan:{ch} off')

    def configure_channel(self, **kwargs):
        """
        configure a channel

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ch       = kwargs.get('channel',    'ch1'   )
        load     = kwargs.get('load',       'off'   )
        freq     = kwargs.get('frequency',  1e3     )
        period   = kwargs.get('period',     None    )
        ampl     = kwargs.get('amplitude',  1.0     )
        offs     = kwargs.get('offset',     0.0     )
        outRange = kwargs.get('range',      None    )
        func     = kwargs.get('function',   'sine'  )

        self.write_configs(
            configs=[
                f'chan {ch}',
                f'func:sine:load {load}',
                f'func:{func}:freq {freq}',
            ]
        )
        ''' override freq if period is given '''
        if period:
            self.write(f'func:{func}:per {period}')

        ''' override amplitude and offset with
            min/max output voltage range instead
        '''
        if len(outRange) == 2:
            self.debug(f'setting output range to {outRange}')
            self.write_configs(
                configs=[
                    f'func:{func}:ampl {ampl}',
                    f'func:{func}:offs {offs}',
                ]
            )
        else:
            self.debug(f'setting output to {ampl} V with {offs} V offset')
            self.write_configs(
                configs=[
                    f'func:{func}:high {outRange[-1]}',
                    f'func:{func}:low {outRange[0]}',
                ]
            )

    def configure_channel_arbitrary(self, **kwargs):
        """
        configure a channel for arbitrary output

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        self.configure_channel(**kwargs)
        ''' get the arbitrary function, default to gaussian '''
        func = kwargs.get('arbitrary_function', 'Gauss')
        funcIdx = AG2062F.built_in_arb.get(func, None)
        ''' arb index returned a value '''
        if funcIdx is not None:
            self.write(f'func:arb:buil {funcIdx}')
        elif '.bin' in func:
            ''' check for a binary file in flash '''
            flashFileListString = self.query('file:file?')
            if func in flashFileListString:
                self.write(f'func:arb:file {func}')
            else:
                raise Exception(
                    f'\'{func}\' does not exist in flash memory!'
                    '\tplease load file into AWG'
                )
        else:
            raise Exception(
                f'\'{func}\' not supported'
            )

    def create_arbitrary_waveform_file(**kwargs) -> str:
        """
        Creates an arbitrary waveform file.

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary

        :returns:   the file name
        :rtype:     str
        """
        data = kwargs.get('data')
        fname = kwargs.get('filename')
        data = np.asarray(data)
        print(f'{data}')
        ''' resample data '''
        if kwargs.get('resample', False):
            numPoints = kwargs.get('numpts', 8192)
            data = signal.resample(data, numPoints)
            print(f'{data}')
            fname = f'resample{numPoints}_{fname}'

        ''' scale to 0 - 12bit max as int '''
        def fscale(d, dmin, dmax):
            return (float(d)-float(dmin))/(float(dmax)-float(dmin))
        data = [fscale(d, min(data), max(data)) for d in data]
        print(f'{data}')
        data = np.asarray(data)*16383.0
        data = [int(d) for d in data]
        print(f'{data}')

        _f = open(fname, 'wb')
        np.asarray(data, dtype=np.uint16).tofile(_f)
        _f.close()

        return fname

    def upload_arbitrary_waveform(self, **kwargs):
        """
        Uploads an arbitrary waveform.

        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ''' check to see if it already exists '''
        fileName = kwargs.get('filename', None)
        flashFileListString = self.query('file:file?')
        fileExistsInFlash = True if fileName in flashFileListString else False

        ''' if the file does not exist in the flash memory, upload it then return '''
        if fileExistsInFlash is False:
            return

        ''' check to see if files match '''
        tempFileName = f'arbw_{datetime.now()}.bin'
        temp = open(tempFileName, 'wb')


        remove(tempFileName)



        ''' if the file does not match, delete it, and upload the new one '''
        pass
