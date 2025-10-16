#!/usr/bin/env python

"""
Generic VISA Intrument interface
"""

import time
from datetime import datetime
from typing import List
import pprint as pp
from pyvisa import (VisaIOError, InvalidSession, VisaIOWarning, log_to_screen, ResourceManager)


def instruments_verbose_log():
    """ debuggibng """
    log_to_screen()

class Instrument: #pylint: disable=too-many-instance-attributes
    """
    an instrument convenience class.
    """
    ignore_list = [
        'start',
        'stop',
        'run'
    ]
    
    def __init__(self, **kwargs):
        """
        constructor
        """
        debug = kwargs.get('debug', False)
        timeout = kwargs.get('timeout', 1000)
        backend = kwargs.get('backend', None)
        if backend is not None:
            self._manager = ResourceManager(backend)
        else:
            self._manager = ResourceManager()

        self.device = None

        self._manufacturer = ''
        self._model = ''
        self._serial_number = ''
        self._version = ''
        self._interface = ''
        self._manufacturer_id = 0x0000
        self._model_id = 0x0000

        self._debug_enable = debug
        self._timeout = timeout
        self._start_time_seconds = round(time.time() * 1000)
        self._start_time_seconds /= 1000.0

    def __inst_init__(self, model, **kwargs):
        serial_number = kwargs.get('serial_number')
        if serial_number:
            self.debug(f'Attempting Connect to {serial_number}', enable=True)
            self.connect(
                serial_number=serial_number,
                include_tcpip=kwargs.get('include_tcpip', False),
                include_rs232=kwargs.get('include_rs232', False)
            )
        else:
            # connect to the first model given
            self.debug(f'No Serial Given, connecting to first {model}', enable=True)
            devices = self.list_devices()
            connected = False
            for device in devices:
                if device.get('model') == model:
                    self.debug(f'Attempt connect to {model} - {device.get("serial_number")}')
                    self.connect(
                        serial_number=device.get('serial_number'),
                        include_tcpip=kwargs.get('include_tcpip', False),
                        include_rs232=kwargs.get('include_rs232', False),
                    )
                    connected = True
                    break
            if connected is False:
                raise Exception(f'Could not connect to {serial_number}')

    @property
    def debug_enable(self) -> bool:
        ''' accessor '''
        return self._debug_enable

    @debug_enable.setter
    def debug_enable(self, value: bool):
        ''' set debug mode '''
        self.debug(f'Debug : {value}', True)
        self._debug_enable = value

    @staticmethod
    def decode_idn(idn: str) -> dict:
        """
        Decodes an idn.

        :param      idn:  The idn
        :type       idn:  str

        :returns:   dictionary of idn parameters
        :rtype:     dict
        """
        idn = idn.replace('\n', '').replace('\r', '').split(',')
        data = {}
        data['manufacturer'] = idn[0]
        data['model'] = idn[1]
        data['serial_number'] = idn[2]
        data['version'] = idn[3]
        return data

    def identify(self):
        """
        identify instrument
        """
        # try with read terminator of \n
        self.device.read_termination = '\n'
        response = self.query('*idn?')
        if response is not None:
            idn = self.decode_idn(response)
            return idn
        # try again with \r read termination
        self.device.read_termination = '\r'
        response = self.query('*idn?')
        if response is not None:
            idn = self.decode_idn(response)
            return idn
        self.debug('IDN Error')
        return None

    def list_devices(self, include_tcpip: bool = False, include_rs232: bool = False) -> List[dict]:
        """
        get list of connected instrument serial numbers

        :param      include_tcpip: flag to include tcpip connected instruments
        :type       include_tcpip: bool

        :returns:   List of idn dictionaries
        :rtype:     List[dict]
        """
        results = []

        self.debug('Looking for USB Connected instruments ...')
        # usb devices
        device_list = self._manager.list_resources(query='USB?*')

        # rs232 devices
        if include_rs232:
            device_list += self._manager.list_resources(query='ASRL?*')

        if include_tcpip:
            self.debug('Looking for TCPIP Connected instruments ...')
            device_list += self._manager.list_resources(query='TCPIP?*')

        _shadow = self.device
        for device in device_list:
            _dev = None
            try:
                _dev = self._manager.open_resource(device)
                self.debug(_dev)
                if _dev is None:
                    continue
            except (InvalidSession, VisaIOError, VisaIOWarning):
                self.debug(f'{_dev} is disconnected or cannot communicate')
            else:
                self.debug(f'IDN - {device}')
                self.device = _dev
                identify = self.identify()
                if identify is None:
                    self.debug(f'Could not Identify {_dev}')
                    continue
                results.append(
                    {
                        **identify,
                        **{
                            'interface': str(_dev).split('::')[0].split(' at ')[1],
                            'device': _dev
                        }
                    }
                )
        self.device = _shadow
        return results

    def connect(
        self,
        serial_number: str,
        include_tcpip: bool = False,
        include_rs232: bool = False,
        model: str = None,
        read_terminator = '\n',
        timeout: int = 5000) -> bool:
        """
        connect to a device

        :param      serial_number:  The serial number
        :type       serial_number:  str
        :param      include_tcpip:  Indicates if the tcpip is included
        :type       include_tcpip:  bool

        :returns:   True if successful, False if not
        :rtype:     bool
        """
        if self.device is not None:
            self.close()
            self.device = None

        self._start_time_seconds = round(time.time() * 1000)
        self._start_time_seconds /= 1000.0

        idn_list = self.list_devices(
            include_tcpip=include_tcpip,
            include_rs232=include_rs232,
        )
        target = None
        for _idn in idn_list:
            if serial_number.lower() == _idn.get('serial_number').lower():
                target = _idn
                pp.pprint(_idn)
                # check for the proper model if given
                if model:
                    if model.lower() == _idn.get('model'):
                        self.device = _idn.get('device')
                        break
                else:
                    self.device = _idn.get('device')
                    break

        if self.device is None:
            self.debug(f'Could not connect to \'{serial_number}\'')
            return False

        self.device.read_termination = read_terminator
        self.device.timeout = timeout

        self._manufacturer = target.get('manufacturer')
        self._model = target.get('model')
        self._serial_number = target.get('serial_number')
        self._version = target.get('version')
        self._interface = target.get('interface')

        return True

    def seconds(self):
        """
        return the amount of time the connection has been open
        in seconds
        """
        time_now = round(time.time() * 1000) / 1000.0
        return time_now - self._start_time_seconds

    def debug(self, data: str, enable: bool = False):
        """
        print to terminal if self._debug == True

        :param      data:  The data
        :type       data:  str
        :param      enable: immediate debug enable
        :type       enable: bool

        :returns:   None
        :rtype:     None
        """
        if self._debug_enable or enable:
            try:
                print(
                    f'{datetime.now().isoformat()} - '+
                    f'{type(self).__name__}(sid:{self.device.session}): '+
                    f'{data}'
                    )
            except (InvalidSession, AttributeError):
                print(
                    f'{datetime.now().isoformat()} - '+
                    f'{type(self).__name__}(-CLOSED-): '+
                    f'{data}'
                )

    @property
    def manufacturer(self):
        """ accessor """
        return self._manufacturer

    @property
    def model(self):
        """ accessor """
        return self._model

    @property
    def serial_number(self):
        """ accessor """
        return self._serial_number

    @property
    def version(self):
        """ accessor """
        return self._version

    def write_configs(self, configs: List[str]):
        ''' write a list of configurations to the instrument'''
        for conf in configs:
            if conf is None:
                continue
            self.write(conf)

    def write_read_configs(self, configs: List[str], verify: bool = False):
        ''' write configs then read them back
            bool verify:    false   - configs not checked,
                            true    - will raise exception
        '''
        self.write_configs(configs)
        for cfg in configs:

            strp_config = cfg.split(' ')
            if strp_config is None:
                continue
            # self.debug(f)
            config = self.device.query(f'*{strp_config[0]}?\n')
            config = None
            self.debug(f'set( {cfg} ) - strp( {cfg.split(' ')} ) - rec( {config} )')


    def query(self, cmd: str, **kwargs):
        """
        read/write opoeration to instrument

        :param      cmd:  The command
        :type       cmd:  str
        """
        if self.device is None:
            return None

        query_ascii = kwargs.get('is_ascii', True)
        query_binary = kwargs.get('is_binary', False)
        if query_ascii and not query_binary:
            try:
                self.debug(f'query( {cmd} )')
                response = self.device.query(cmd)
                response = response.replace('\r', '').replace('\n', '')
                self.debug(f'resp( {response} )')
                return response
            except (InvalidSession, VisaIOError, VisaIOWarning) as _e:
                self.debug(f'QUERY Error: {_e}')
                return None
        else:
            try:
                self.debug(f'query( {cmd} )')
                response = self.device.query_binary_values(
                    cmd,
                    datatype=kwargs.get('datatype', 'd'),
                    is_big_endian=kwargs.get('is_big_endian', True)
                )
                self.debug(f'resp( {response} )')
                return response
            except (InvalidSession, VisaIOError, VisaIOWarning) as _e:
                self.debug(f'QUERY Error: {_e}')
                return None

    def write(self, cmd: str):
        """
        write data to instrument

        :param      cmd:  The command
        :type       cmd:  str
        """
        if self.device is None:
            return None
        try:
            self.debug(f'write( {cmd} )')
            return self.device.write(cmd)
        except (InvalidSession, VisaIOError, VisaIOWarning) as _e:
            self.debug(f'WRITE Error: {_e}')
            return None

    def read(self, cmd: str):
        """
        read data from instrument

        :param      cmd:  The command
        :type       cmd:  str
        """
        if self.device is None:
            return None
        try:
            self.debug(f'read( {cmd} )')
            return self.device.read(cmd)
        except (InvalidSession, VisaIOError, VisaIOWarning) as _e:
            self.debug(f'READ Error: {_e}')
            return None

    def reset(self):
        """
        Resets the instrument.
        """
        if self.device is None:
            return None
        try:
            return self.write('*rst')
        except (InvalidSession, VisaIOError, VisaIOWarning):
            return None

    def close(self, **kwargs):
        """
        close instrument
        """
        if self.device is None:
            return
        try:
            if kwargs.get('reset', False):
                self.reset()
            self.write('system:local')
            self.device.before_close()
            self.device.close()
        except InvalidSession:
            self.debug(
                'Attempt Close on InvalidSession',
                enable=True
            )
