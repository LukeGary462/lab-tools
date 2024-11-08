#!/usr/bin/env python

"""
common funcs
"""
import re
from typing import List

def get_numbers_from_line(line: str) -> List[float]:
    """
    Gets the numbers from line.

    :param      line:  The line
    :type       line:  str

    :returns:   The numbers from line.
    :rtype:     List of Floats
    """
    numerics = \
        r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?'
    regex = re.compile(numerics, re.VERBOSE)
    return [float(res) for res in regex.findall(line) if res]


