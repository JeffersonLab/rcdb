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
    def __init__(self, name):
        self.lines = []
        self.name = name


class CodaRunLogParseResult(object):
    """ Class is responsible for holding data for daq update """

    def __init__(self):
        self.sections = {}
        self.trigger_equation = []
        self.trigger_type = []

    @property
    def section_names(self):
        return self.sections.keys()

    def add_section(self, section):
        self.sections[section.name] = section


def parse_file(filename):
    lines = []
    with open(filename, "r") as ins:
        lines = ins.readlines()

    result = CodaRunLogParseResult()
    section = CodaRunLogSection('')
    result.add_section(section)

    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            continue

        if line in section_names:
            section = CodaRunLogSection(line)
            result.add_section(section)
        else:
            section.lines.append(line)

            if line.startswith('TRIG_EQ'):
                result.trigger_equation.append(line.split()[1:])

            if line.startswith('TRIG_TYPE'):
                result.trigger_type.append(line.split()[1:])

    return result
