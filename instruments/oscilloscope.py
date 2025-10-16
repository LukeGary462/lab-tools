#!/usr/bin/env python

"""
oscilloscopes
"""

from instruments.instrument import Instrument
from pyvisa import (VisaIOError, InvalidSession, VisaIOWarning, log_to_screen, ResourceManager)
import pprint as pp
import numpy as np

class OscilloscopeModels:
    """
    This class describes oscilloscope models.
    """
    def __init__(self):
        self.models = {}
        self.models['DS1074Z'] = DS1074Z
        self.models['DSOX1102G'] = DSOX1102G
        self.models['MSOX3032T'] = MSOX3032T
        self.models['WaveRunner8104MS'] = WaveRunner8104MS
        self.models['WaveAce2012'] = WaveAce2012

    def get(self, model: str) -> Instrument:
        """
        Gets the specified model.

        :param      model:  The model
        :type       model:  str

        :returns:   oscilloscope class
        :rtype:     Instrument
        """
        return self.models.get(model, None)

    def is_valid(self, model: str) -> bool:
        return model in self.models.keys()

def connect_to_oscilloscope(
        model: str,
        scope_serial: str = None,
        rs232: bool = False,
        tcpip: bool = False) -> object:
    """
    Connects to oscilloscope.

    :param      model:         The model
    :type       model:         str
    :param      scope_serial:  The oscilloscope serial number
    :type       scope_serial:  str
    :param      tcpip:         The tcpip
    :type       tcpip:         bool

    :returns:   oscilloscope obbject if model is valid, none if not
    :rtype:     object
    """
    scope_obj = None
    scope = OscilloscopeModels().get(model)
    scope.debug_enable = True
    if scope and scope_serial:
        try:
            scope_obj = scope(
                serial_number=scope_serial,
                include_tcpip=tcpip,
                include_rs232=rs232,
                )
        except (VisaIOError, VisaIOWarning, InvalidSession):
            raise Exception(f'Could not connect to scope {model}:{scope_serial}')

    if scope:
        try:
            scope_obj = scope(
                include_tcpip=tcpip,
                include_rs232=rs232,
                )
        except (VisaIOError, VisaIOWarning, InvalidSession):
            raise Exception(f'Could not connect to scope {model}:{scope_serial}')

    return scope_obj

class WaveAce2012(Instrument):
    '''Teledyne Lecroy WaveAce 2012 Oscilloscope

    100MHz analog bandwidth, 2GS/s
    Only basic configuration and waveform capture supported
    https://cdn.teledynelecroy.com/files/manuals/wa1k2k_remote-control_manual.pdf
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='WaveAce2012', **kwargs)

    def default_setup(self):
        '''default configuration for a scope

        set channels active, 10x atten, bandwidth limiting, c1 trigger source,
        dc coupling, 1v/div, trigger magnitude at 0.5v, rising edge trigger,
        assume user is going to connect probes to probe comp source then compensate probes
        '''
        debug_state = self._debug_enable
        self._debug_enable = True
        self.write_configs(
            configs=[
                'stop',

                'tdiv 100us',

                'c1:tra on',
                'c1:attn 10',
                'c1:vdiv 1',
                'c1:bwl off',
                'c1:cpl d1m',

                'c2:tra on',
                'c2:attn 10',
                'c2:vdiv 1',
                'c2:bwl off',
                'c2:cpl d1m',

                'c1:trcp dc',
                'c1:trlv 0.5',
                'trmd norm',

                'c1:ofst 0.0',
                'c2:ofst -3.0',
                'run'
            ]
        )
        self._debug_enable = debug_state

    def capture_setup(self, ch: int = 1, **kwargs):
        debug_state = self._debug_enable
        self._debug_enable = True
        self.write_configs(
            configs=[
                'stop',
                f'tdiv {kwargs.get("tdiv", "250us")}',
                'c1:tra on',
                'c1:attn 10',
                'c1:vdiv 1',
                'c1:bwl off',
                'c1:cpl d1m',
                'c1:trcp dc',
                f'c1:trlv {kwargs.get("trlv", 0.5)}',
                'trmd single',
                'c1:ofst 0.0',
                'run'
            ]
        )
        self._debug_enable = debug_state

    def get_waveform(self, ch: int = 1, **kwargs):
        t = None
        data = None
        preamble = None
        sample_rate = None

        data = self.query(
            cmd=f'C{1}:wf? all',
            is_binary=True
        )
        return  {
                'time': t,
                'data': data,
                'preamble': preamble,
                'sample_rate': sample_rate
                }

    def get_timebase(self) -> float:
        command = 'tdiv'
        readback = self.device.query(command.lower())
        readback = readback\
                    .lower()\
                    .replace(command,"")
        return float(readback)


class WaveRunner8104MS(Instrument):
    '''Teledyne Lecroy Waverunner 8104-MS Oscilloscope

    1GHz Analog Bandwidth Scope, Only basic configuration and
    acquisition functions supported. See Programming manual for
    more complex functions and use the superclass write/config methods.
    See the test examples for a surrogate usecase.
    https://cdn.teledynelecroy.com/files/manuals/waverunner-8000-operators-manual.pdf


    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='WaveRunner8104MS', **kwargs)
        print('Consider using the lecroydso python package directly instead of this for now...')



    def get_waveform(self, ch, **kwargs):
        print("Not Supported Yet")
        pass

class DS1074Z(Instrument):
    """
    This class describes a Rigol ds1074z scope.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='DS1074Z', **kwargs)

    def get_waveform(self, ch, **kwargs):
        '''get waveform data'''
        self._debug_enable = True
        self.debug(f'waveform capture start : \n\tkwargs{kwargs}')
        self.write_configs(
            configs=[
                f'wav:sour chan{ch}',
                'wav:mode raw',
                'wav:form byte',
                'wav:star raw',
                'wav:stop raw'
            ]
        )
        sample_rate = self.query('acq:srate?')
        sample_rate = float(sample_rate)
        preamble_resp = self.query('wav:pre?')
        preamble_keys = [
            'format', 'type', 'points',
            'count', 'xinc', 'xorigin',
            'xref', 'yinc', 'yorigin',
            'yref'
        ]
        preamble = {}
        for idx, p in enumerate(preamble_resp.split(',')):
            preamble[preamble_keys[idx]] = float(p)
        self.debug(pp.pformat(preamble))
        timestep    = preamble.get('xinc')
        timestart   = preamble.get('xorigin')

        data = self.device.query_binary_values(
            'wav:data?\n',
            datatype='B',
            is_big_endian=True
        )
        data = data[11:-1]
        data = [
            float(d)*float(preamble.get('yinc', 1.0))
            for d in data
        ]
        self.debug(f'first sample : {int(data[0])}')
        self.debug(f'last sample  : {int(data[-1])}')
        t = []
        for idx, d in enumerate(data):
            t.append(timestart+(idx*timestep))

        return  {
                'time': t,
                'data': data,
                'preamble': preamble,
                'sample_rate': sample_rate
                }

    def get_waveform_ascii(self, ch: int, **kwargs):
        """
        Gets the waveform.

        :param      ch:      channel index
        :type       ch:      int
        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        ''' read the trace data in ascii and let the scope
            format to floats of the sampled voltages
        '''
        self._debug_enable = True
        self.debug(f'waveform capture start : \n\tkwargs{kwargs}')
        waveform_mode = kwargs.get('mode', 'norm')
        self.write_configs(
            configs=[
                f'wav:sour chan{ch}',
                f'wav:mode {waveform_mode}',
                'wav:form ascii',
            ]
        )
        sample_rate = float(self.query('acq:srate?'))
        preamble_resp = self.query('wav:pre?')
        preamble_keys = [
            'format', 'type', 'points',
            'count', 'xinc', 'xorigin',
            'xref', 'yinc', 'yorigin',
            'yref'
        ]
        preamble = {}
        for idx, p in enumerate(preamble_resp.split(',')):
            preamble[preamble_keys[idx]] = float(p)
        self.debug(pp.pformat(preamble))
        timestep    = preamble.get('xinc')
        timestart   = preamble.get('xorigin')
        self.debug_enable = False
        data = self.query(
            f'wav:data?',
            is_ascii=True,
        )
        self.debug_enable = True
        ''' data is returned as csv, char by char. join all chars, then split on commas '''
        data = ''.join(data).split(',')
        ''' throw out the header since it just describes the number of datapoints'''
        data[0] = '.'+data[0].split('.')[-1]
        self.debug(f'first sample : {data[0]}')
        self.debug(f'last sample  : {data[-1]}')
        data = [float(d) for d in data]
        t = []
        for idx, d in enumerate(data):
            t.append(timestart+(idx*timestep))

        return  {
                'time': t,
                'data': data,
                'preamble': preamble,
                'sample_rate': sample_rate
                }

class MSOX3032T(Instrument):
    """
    This class describes a msox 3032 t.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='MSO-X 3032T', **kwargs)

    def get_waveform(self, ch, **kwargs):
        """
        Gets the waveform.

        :param      ch:      channel name
        :type       ch:      string
        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        acq_source = kwargs.get('acq_source', 'raw')
        self.debug(f'waveform capture start : \n\tkwargs{kwargs}')
        self.write_configs(
            configs=[
                f'wav:sour chan{ch}',
                f'wav:points:mode {acq_source}',
                'wav:form byte',
                'wav:uns 1',
            ]
        )
        sample_rate = float(self.query('acq:srate?'))
        preamble_resp = self.query('wav:pre?')
        preamble_keys = [
            'format', 'type', 'points',
            'count', 'xinc', 'xorigin',
            'xref', 'yinc', 'yorigin',
            'yref'
        ]
        preamble = {}
        for idx, p in enumerate(preamble_resp.split(',')):
            preamble[preamble_keys[idx]] = float(p)
        self.debug(pp.pformat(preamble))
        timestep    = preamble.get('xinc')
        timestart   = preamble.get('xorigin')

        data = self.device.query_binary_values(
            'wav:data?',
            datatype='B',
        )
        print(f'{data[0:100]}')
        self.debug(f'first sample : {data[0]}')
        self.debug(f'last sample  : {data[-1]}')
        yinc = float(preamble.get('yinc', 1.0))
        yorg = float(preamble.get('yorigin', 0.0))
        yref = float(preamble.get('yref', 1.0))
        data = [yorg+((float(d)-yref)*yinc) for d in data]
        t = []
        for idx, d in enumerate(data):
            t.append(timestart+(idx*timestep))

        return  {
                'time': t,
                'data': data,
                'preamble': preamble,
                'sample_rate': sample_rate
                }

    def _get_preamble(self) -> dict:
        preamble_resp = self.query('wav:pre?')
        preamble_keys = [
            'format', 'type', 'points',
            'count', 'xinc', 'xorigin',
            'xref', 'yinc', 'yorigin',
            'yref'
        ]
        preamble = {}
        for idx, p in enumerate(preamble_resp.split(',')):
            preamble[preamble_keys[idx]] = float(p)
        self.debug(pp.pformat(preamble))
        return preamble

    def get_digitized_waveform(self, ch, **kwargs):
        """
        Gets the waveform from digitizer.
        :param      ch:      channel name
        :type       ch:      string
        :param      kwargs:  The keywords arguments
        :type       kwargs:  dictionary
        """
        requested_sample_rate = float(kwargs.get('sample_rate', 20e6))
        requested_sample_duration = float(kwargs.get('sample_duration', None))

        ''' set the sample rate '''
        sample_rate = self.set_sample_rate(
            sample_rate=requested_sample_rate,
        )

        ''' calculate the minimum number of points needed given the
            requested sample duration. This will keep captures fast when xfering
            over scpi
        '''
        valid_memory_depths = [
            100,250,500,1000,
            2000,5000,10000,20000,
            50000,100000,200000,500000,
            1000000,2000000,4000000,8000000,
        ]
        mdepth_to_use = 100
        num_samples_needed = sample_rate * requested_sample_duration
        self.debug(f'samples needed : {num_samples_needed}')
        for idx, mdepth in enumerate(valid_memory_depths):
            if num_samples_needed > mdepth:
                continue
            if num_samples_needed <= mdepth:
                mdepth_to_use = valid_memory_depths[idx+1]
                break
        self.debug(f'setting mdepth to : {mdepth_to_use} samples')
        self.write(f'ACQ:POINT:ANAL {mdepth_to_use}')
        ''' set time range of full window '''
        self.write(f'tim:range {requested_sample_duration}')

        self.write_configs(
            configs=[
                f'wav:sour chan{ch}',
                f'wav:points:mode raw',
                'wav:form byte',
                'wav:uns 1',
            ]
        )

        self.write(f'dig chan{ch}')
        data = self.device.query_binary_values(
            'wav:data?',
            datatype='B',
        )
        yinc        = float(self.query('wav:yinc?'))
        yorg        = float(self.query('wav:yor?'))
        yref        = float(self.query('wav:yref?'))
        timestep    = float(self.query('wav:xinc?'))
        timestart   = float(self.query('wav:xor?'))
        data = [yorg+((float(d)-yref)*yinc) for d in data]
        t = []
        for idx, d in enumerate(data):
            t.append(timestart+(idx*timestep))

        return  {
                'time': t,
                'data': data,
                'sample_rate': sample_rate,
                'preamble': {
                        'yinc': yinc,
                        'yorg': yorg,
                        'yref': yref,
                        'xinc': timestep,
                        'xorg': timestart,
                    }
                }

    def set_sample_rate(self, **kwargs) -> float:
        '''
            set the sample rate of the scope
        '''
        requested_sample_rate = kwargs.get('sample_rate')
        requested_sample_duration = kwargs.get('sample_duration', None)
        # Sampling Rate = Memory Depth / Time on Screen
        current_sample_rate = float(self.query('acq:srate?'))
        if float(current_sample_rate) == float(kwargs.get('sample_rate')):
            self.debug('Sample Rate already correct')
            return current_sample_rate
        self.write(f'ACQ:SRAT:ANAL {requested_sample_rate}')
        return float(self.query('acq:srate?'))

class DSOX1102G(Instrument):
    """
    This class describes a dsox1102g keysight oscilloscope.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__inst_init__(model='DSO-X 1102G', **kwargs)

    def set_bode_enable(self, **kwargs):
        enable = kwargs.get('enable', 0)
        self.write(f'FRAN:ENAB {enable}')
        enable = self.query(f'FRAN:ENAB?')
        self.debug(enable)

    def set_bode_freq_start(self, **kwargs):
        startfreq = kwargs.get('startfreq', 10)
        units = kwargs.get('units', 'Hz')
        self.write(f'FRAN:FREQ:STAR {startfreq}{units}')
        startfreq = self.query(f'FRAN:FREQ:STAR?')
        self.debug(startfreq)

    def set_bode_freq_stop(self, **kwargs):
        stopfreq = kwargs.get('stopfreq', 1000)
        units = kwargs.get('units', 'kHz')
        self.write(f'FRAN:FREQ:STOP {stopfreq}{units}')
        stopfreq = self.query(f'FRAN:FREQ:STOP?')
        self.debug(stopfreq)

    def set_bode_sourcein(self, **kwargs):
        inchan = kwargs.get('inchan', 1)
        self.write(f'FRAN:SOUR:INP {inchan}')
        inchan = self.query(f'FRAN:SOUR:INP?')
        self.debug(inchan)

    def set_bode_sourceout(self, **kwargs):
        outchan = kwargs.get('outchan', 2)
        self.write(f'FRAN:SOUR:OUTP {outchan}')
        outchan = self.query(f'FRAN:SOUR:OUTP?')
        self.debug(outchan)

    def set_bode_genload(self, **kwargs):
        genload = kwargs.get('genload', 'ONEM')
        self.write(f'FRAN:WGEN:LOAD {genload}')
        genload = self.query(f'FRAN:WGEN:LOAD?')
        self.debug(genload)

    def set_bode_genvolt(self, **kwargs):
        genvolt = kwargs.get('genvolt', 1)
        self.write(f'FRAN:WGEN:VOLT {genvolt}')
        genvolt = self.query(f'FRAN:WGEN:VOLT?')
        self.debug(genvolt)

    def set_bode_run(self):
        self.write(f'FRAN:RUN')

    def get_stdevtstatusreg(self): #bit 0 will go HIGH when FRAN process is complete
        stdevtstatusreg = self.query(f'*ESR?')
        self.debug(stdevtstatusreg)
        return stdevtstatusreg

    def get_bode_status(self):
        status = self.query(f'FRAN?')
        self.debug(f'status')
        self.debug(status)

    def get_bode_data(self):
        #self.debug(f'Getting bode data')
        #wavfor = self.write(f'SAVE:WAV:FORM?')
        #print(wavfor)
        #self.debug(wavfor)
        data = self.query(
            f'FRAN:DATA?',
            #is_ascii=True,
            is_binary=True,
            datatype='s',
            #is_big_endian = False
            #container = numpy.array
        )
        # data = self.query_binary_values(
            # f'FRAN:DATA?',
            # datatype = 'd',
            # is_big_endian = True,

        # )
        return data

    def set_vertical_scale(self, channel: int = 1, **kwargs):
        scale = kwargs.get('scale', 1.0)
        units = kwargs.get('units', 'V')
        self.write(f'CHAN{channel}:SCAL {scale}{units}')
        scale = self.query(f'CHAN{channel}:SCAL?')
        self.debug(scale)

    def set_horizontal_scale(self, **kwargs):
        timescale = kwargs.get('timescale', 0.001)
        self.write(f'TIM:SCAL {timescale}')
        timescale = self.query(f'TIM:SCAL?')
        self.debug(timescale)

    def set_waveform_byte_order(self, **kwargs):
        byte_order = kwargs.get('byte_order', 'MSBFirst')
        self.write(f'WAV:BYT {byte_order}')
        byte_order = self.query(f'WAV:BYT?')
        self.debug(byte_order)

    def set_waveform_format(self, **kwargs):
        wfformat = kwargs.get('wfformat', 'WORD')
        self.write(f'WAV:FORM {wfformat}')
        wfformat = self.query(f'WAV:FORM?')
        self.debug(wfformat)

    def set_waveform_source(self, **kwargs):
        wfsource = kwargs.get('wfsource', 'CHAN1')
        self.write(f'WAV:SOUR {wfsource}')
        wfsource = self.query(f'WAV:SOUR?')
        self.debug(wfsource)

    def set_waveform_points_mode(self, **kwargs):
        pointsmode = kwargs.get('pointsmode', 'NORM')
        self.write(f'WAV:POIN:MODE {pointsmode}')
        pointsmode = self.query(f'WAV:POIN:MODE?')
        self.debug(pointsmode)

    def get_waveform_count(self):
        wfcount = self.query(f'WAV:COUN?')
        self.debug(wfcount)
        return wfcount

    def get_waveform_format(self):
        wfformat = self.query(f'WAV:FORM?')
        self.debug(wfformat)
        return wfformat

    def get_xinc(self):
        xinc = self.query(f'WAV:XINC?')
        self.debug(xinc)
        return float (xinc)

    def get_xor(self):
        xor = self.query(f'WAV:XOR?')
        self.debug(xor)
        return float (xor)

    def get_yinc(self):
        yinc = self.query(f'WAV:YINC?')
        self.debug(yinc)
        return float (yinc)

    def get_yor(self):
        yor = self.query(f'WAV:YOR?')
        self.debug(yor)
        return float (yor)

    def get_yref(self):
        yref = self.query(f'WAV:YREF?')
        self.debug(yref)
        return float (yref)

    def do_query_ieee_block(self, cmd:str, **kwargs):
        result = self.device.query_binary_values(cmd, datatype='s', is_big_endian=True)
        self.debug(result)
        return result

    def measure_vmax_FFT(self):
        self.write(f'MEAS:VMAX FFT')
        vmax = self.query(f'MEAS:VMAX? FFT')
        self.debug(vmax)
        return (vmax)

    # def get_measurement_vmax_FFT(self, **kwargs):
        # #source = kwargs.get('SOURCE', 'FFT')
        # vmax = self.query(f'MEAS:VMAX')
        # self.debug(vmax)
        # return (vmax)

    def measure_vpp(self, **kwargs):
        chan = kwargs.get('chan', 1)
        self.write(f'MEAS:VPP CHAN {chan}')
        vpp = self.query(f'MEAS:VPP? CHAN{chan}')
        self.debug(vpp)
        return (vpp)

    def measure_vrms(self, **kwargs):
        chan = kwargs.get('CHAN', 1)
        self.write(f'MEAS:VRMS CHAN {chan}')
        vrms = self.query(f'MEAS:VRMS? CHAN{chan}')
        self.debug(vrms)
        return (vrms)

    def measure_freq(self, **kwargs):
        chan = kwargs.get('chan', 1)
        self.write(f'MEAS:FREQ CHAN {chan}')
        freq = self.query(f'MEAS:FREQ? CHAN{chan}')
        self.debug(freq)
        return (freq)

    def set_wgen_freq(self, **kwargs):
        frequency = kwargs.get('FREQ', 1000)
        self.write(f'WGEN:FREQ {frequency}')
        frequency = self.query(f'WGEN:FREQ?')
        self.debug(frequency)

    def set_wgen_volt(self, **kwargs):
        voltage = kwargs.get('VOLT', 1)
        self.write(f'WGEN:VOLT {voltage}')
        voltage = self.query(f'WGEN:VOLT?')
        self.debug(voltage)

    def set_wgen_offs(self, **kwargs):
        offset = kwargs.get('OFFS', 1)
        self.write(f'WGEN:VOLT:OFFS {offset}')
        offset = self.query(f'WGEN:VOLT:OFFS?')
        self.debug(offset)
