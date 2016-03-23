import logging
import os
import xml.etree.ElementTree as Et
from datetime import datetime
from rcdb.log_format import BraceMessage as Lf

# Setup logger
log = logging.getLogger('rcdb.coda_parser')         # create run configuration standard logger


# run config file name in rtvs collection
RUN_CONFIG_RTV = '%(config)'

section_names = [
    'TRIGGER',
    'GLOBAL',
    'FCAL',
    'BCAL',
    'TOF',
    'ST',
    'TAGH',
    'TAGM',
    'PS',
    'PSC',
    'TPOL',
    'CDC',
    'FDC',
]

class CodaRunLogSection(object):
    def __init__(self):
        self.items

class CodaRunLogParseResult(object):
    """ Class is responsible for holding data for daq update """

    def __init__(self):
        self.sections = []


def parse_file(filename):
    with open(filename, "r") as ins:
        lines = ins.readlines()
