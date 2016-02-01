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
        is_section_name = False
        current_section = ""

        for index,line in enumerate(lines):

            if line.startswith('----') or line.startswith('===='):
                continue

            tokens = shlex.split(line)
            if not tokens:
                continue














class ConfigParseResult:
