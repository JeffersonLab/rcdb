import shlex

SECTION_GLOBAL="GLOBAL"
SECTION_TRIGGER="TRIGGER"
SECTION_HEADER="=========================="

section_names = [SECTION_GLOBAL, SECTION_TRIGGER, ]

class ConfigParser:
    """
    Parses config file
    """



    def __init__(self):
        self.sections = {}
        self.found_section_names = []

    def parse(self, content):
        """
        :param content: Content to parse
        :type content: str
        :return:
        """

        lines = [l.strip() for l in content.splitlines() if l]
        current_section = ""

        for line in lines:

            if line.startswith('----') or line.startswith('===='):
                continue

            tokens = shlex.split(line)
            if not tokens:
                continue

            if tokens[0] in section_names[l]














class ConfigParseResult:
