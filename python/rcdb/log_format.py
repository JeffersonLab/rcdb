
class BraceMessage(object):
    """Class for curly brace formatting for logging
    @see http://stackoverflow.com/questions/13131400/logging-variable-data-with-new-format-string
    """
    def __init__(self, fmt, *args, **kwargs):
        self.fmt = fmt
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.fmt.format(*self.args, **self.kwargs)
