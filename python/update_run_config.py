import json
import logging

from rcdb import UpdateContext, UpdateReasons, DefaultConditions
from halld_rcdb.run_config_parser import HallDMainConfigParseResult
from rcdb.log_format import BraceMessage as Lf
from rcdb.provider import RCDBProvider


# Setup logger
log = logging.getLogger('rcdb.update_run_config')         # create run configuration standard logger


def update_run_config_conditions(context, parse_result):
    """
    Opens and parses coda file

    :return: None
    """

    # read xml file and get root and run-start element

    # Some assertions in the beginning
    assert isinstance(parse_result, HallDMainConfigParseResult)
    assert isinstance(context, UpdateContext)
    assert isinstance(context.db, RCDBProvider)
    db = context.db

    conditions = []

    # --- TRIGGER ---

    # Trigger equation
    if parse_result.trigger_eq is not None:
        conditions.append(('trigger_eq', json.dumps(parse_result.trigger_eq)))

    # Trigger type
    if parse_result.trigger_type is not None:
        conditions.append(('trigger_type', json.dumps(parse_result.trigger_type)))

    # --- CDC ---

    # Set the run as not properly finished (We hope that the next section will
    if parse_result.cdc_fadc125_mode is not None:
        conditions.append(('cdc_fadc125_mode', parse_result.cdc_fadc125_mode))

    print context.run

    # SAVE CONDITIONS
    db.add_conditions(context.run, conditions, replace=True)


