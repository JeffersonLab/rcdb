import ast
from timeit import default_timer
from token import NAME

from ply.lex import LexToken

import rcdb
import rcdb.lexer
from rcdb import RCDBProvider
from rcdb.model import ConditionType, Run, Condition
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, aliased
import shlex
import ast

from rcdb.stopwatch import StopWatchTimer

db = rcdb.RCDBProvider("mysql://rcdb@127.0.0.1/rcdb")

"""
.session \
.query(Run) \
.options(subqueryload(Run.conditions)) \
.filter(Run.number == run_number) \
.first()
"""

import logging

# custom tree formatter
class TreeFormatter(logging.Formatter):
    formatPrefix = {} # map loggername, formatPrefix

    def format(self, record):
        s = ""
        # first time this name is encountered: create the prefix and print the name
        if not record.name in self.formatPrefix:
            f = self.getFormatPrefix(record)
            s += "%s \"%s\"\n" % (f, record.name)

        # print the actual message
        s += "%s %s: %s" % (self.formatPrefix[record.name], record.levelname, record.msg)
        return s


    # create the format prefix for the given package name
    # (stored in self.formatPrefix[record.name])
    # and return the first line to print
    def getFormatPrefix(self, record):
        depth = record.name.count(".")
        self.formatPrefix[record.name] = "   |" * (depth+1)

        if depth == 0:
            return "<--"

        return "%so<--" % ( ("   |" * depth)[:-1])

# use this to create the first level logger
def createTreeLogger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(TreeFormatter())
    logger.addHandler(ch)
    return logger


if __name__ == '__main__':

    logger_a = createTreeLogger("a") # first level: use createLogger
    # then create your loggers as always
    logger_a_b = logging.getLogger("a.b")
    logger_a_b_c = logging.getLogger("a.b.c")
    logger_a_b_c_d = logging.getLogger("a.b.c.d")


    logger_a.debug("One")

    logger_a_b.warning("two")
    logger_a_b.warning("three")

    logger_a_b_c.critical("Four")

    logger_a_b.warning("Five")
    logger_a.warning("Six")
    logger_a_b_c_d.warning("absd")

    sw = StopWatchTimer()
    runs = db.select_runs("@is_production", 0, 20000)
    sw.stop()
    print sw.elapsed, len(runs)

    sw = StopWatchTimer()
    runs = db.select_runs("@is_cosmic", 0, 20000)
    sw.stop()
    print sw.elapsed, len(runs)

    sw = StopWatchTimer()
    runs = db.select_runs("@is_production", 0, 20000)
    sw.stop()
    print sw.elapsed, len(runs)

