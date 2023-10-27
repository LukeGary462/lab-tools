#!/usr/bin/env python
# python 3
#pylint: disable=import-error
##    @file:    instrument.py
#     @name:    Luke Gary
#  @company:    RyeEffectsResearch
#     @date:    2020/3/10
################################################################################
# @copyright
#   Copyright 2020 RyeEffectsResearch as an  unpublished work.
#   All Rights Reserved.
#
# @license The information contained herein is confidential
#   property of RyeEffectsResearch. The user, copying, transfer or
#   disclosure of such information is prohibited except
#   by express written agreement with RyeEffectsResearch.
################################################################################

"""
Generic VISA Intrument interface
"""

import time

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
    def __init__(self, debug: bool = False, timeout: int = 1000, backend=None):
        """
        constructor
        """
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

        self._debug_enable = debug
        self._timeout = timeout
        self._start_time_seconds = round(time.time() * 1000)
        self._start_time_seconds /= 1000.0

    @property
    def debug_enable(self) -> bool:
        ''' accessor '''
        return self._debug_enable

    @debug_enable.setter
    def debug_enable(self, value: bool):
        ''' set debug mode '''
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
        response = self.query('*idn?')
        if response is not None:
            idn = self.decode_idn(response)
            return idn
        self.debug('IDN Error')
        return None

    def list_devices(self, include_tcpip: bool = False) -> List[dict]:
        """
        get list of connected instrument serial numbers

        :param      include_tcpip: flag to include tcpip connected instruments
        :type       include_tcpip: bool

        :returns:   List of idn dictionaries
        :rtype:     List[dict]
        """
        results = []

        self.debug('Looking for USB Connected instruments ...')
        device_list = self._manager.list_resources(query='USB?*')
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

    def connect(self, serial_number: str, include_tcpip: bool = False) -> bool:
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

        idn_list = self.list_devices(include_tcpip=include_tcpip)
        target = None
        for _idn in idn_list:
            if serial_number.lower() == _idn.get('serial_number').lower():
                target = _idn
                pp.pprint(_idn)
                self.device = _idn.get('device')
                break

        if self.device is None:
            self.debug(f'Could not connect to \'{serial_number}\'')
            return False

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
                    f'{self.seconds():0.4f} - '+
                    f'{type(self).__name__}(sid:{self.device.session}): '+
                    f'{data}'
                    )
            except (InvalidSession, AttributeError):
                print(
                    f'{self.seconds():0.4f} - '+
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

    def query(self, cmd: str):
        """
        read/write opoeration to instrument

        :param      cmd:  The command
        :type       cmd:  str
        """
        if self.device is None:
            return None
        try:
            self.debug(f'query( {cmd} )')
            response = self.device.query(cmd)
            response = response.replace('\r', '').replace('\n', '')
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

    def close(self):
        """
        close instrument
        """
        if self.device is None:
            return
        try:
            self.write('system:local')
            self.device.before_close()
            self.device.close()
        except InvalidSession:
            self.debug(
                'Attempt Close on InvalidSession',
                enable=True
            )
