import shlex


class ConfigSection(object):
    def __init__(self, name):
        self.name = name
        self.rows = []
        self.entities = {}


class ConfigFileParseResult(object):
    """
    Result of parsing the config file
    """

    def __init__(self, section_names):
        self.section_names = section_names
        self.sections = {}
        self.found_section_names = []


def parse_file(filename, section_names):
    """
    Opens and parses config file

    :return: ConfigParserResult (it is filled after parsing the file)
    """

    with file(filename) as f:
        content = f.read()
    return parse_content(content, section_names)


def parse_content(content, section_names):
    """
    :param section_names: List of section names. Like TRIGGER, FDC, CDC ...
    :param content: Content to parse
    :type content: str
    :return: ConfigParserResult
    """
    result = ConfigFileParseResult(section_names)

    lines = [l.strip() for l in content.splitlines() if l]
    current_section = None

    for line in lines:

        if line.startswith('----') or line.startswith('===='):
            continue

        # Split tokens by lexical rules
        tokens = shlex.split(line, True)

        # Skip if there is no tokens
        if not tokens:
            continue

        # Is this a section name?
        if tokens[0] in section_names:
            current_section = ConfigSection(tokens[0])
            result.sections[current_section.name] = current_section
            result.found_section_names.append(current_section.name)
            continue

        # If we are here, it is a regular line. Is there defined section?
        if current_section is None:
            continue

        current_section.rows.append(tokens)

        if len(tokens) > 1:
            if len(tokens) == 2:
                current_section.entities[tokens[0]] = tokens[1]
            else:
                current_section.entities[tokens[0]] = tokens[1:]

    return result





















#class ConfigParseResult:
