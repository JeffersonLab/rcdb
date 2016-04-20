import rcdb.config_parser
from rcdb.config_parser import ConfigFileParseResult


section_names = ["TRIGGER", "GLOBAL", "FCAL","BCAL","TOF","ST","TAGH", "TAGM", "PS", "PSC", "TPOL", "CDC", "FDC"]


class HallDMainConfigParseResult(object):

    def __init__(self, config_parse_result):
        assert isinstance(config_parse_result, ConfigFileParseResult)
        self.config_parse_result = config_parse_result


def parse_file(file_name):

    parse_result = rcdb.config_parser.parse_file(file_name, section_names)

    result = HallDMainConfigParseResult(parse_result)






