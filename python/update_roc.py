import json
import logging
import os

from rcdb import UpdateContext, UpdateReasons, DefaultConditions
from halld_rcdb.run_config_parser import HallDMainConfigParseResult
from halld_rcdb.roc_config_finder import find_roc_configuration_files
from rcdb.log_format import BraceMessage as Lf
from rcdb.provider import RCDBProvider


# Setup logger
log = logging.getLogger('rcdb.update_roc')         # create run configuration standard logger


def add_roc_configuration_files(context, parse_result):
    """
    Finds and adds ROC configuration files

    :return: None
    """

    # read xml file and get root and run-start element

    # Some assertions in the beginning
    assert isinstance(parse_result, HallDMainConfigParseResult)
    assert isinstance(context, UpdateContext)
    assert isinstance(context.db, RCDBProvider)
    db = context.db

    infos = []

    try:
        infos = find_roc_configuration_files(parse_result)
    except Exception as ex:
        log.error("Error finding roc configuration files, '{}'".format(ex))

    for info in infos:
        log.debug(Lf("Adding roc configuration files for '{}'", info.name))
        for file_path in info.final_files:
            if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
                log.debug(Lf("Adding roc configuration files for '{}'", file_path))

                #    db.add_configuration_file(run.number,
                #                              file_path,
                #                              importance=ConfigurationFile.IMPORTANCE_LOW)


