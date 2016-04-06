

# Setup logger
import logging

from rcdb import UpdateContext, UpdateReasons
from rcdb.coda_parser import CodaRunLogParseResult
from rcdb.model import ConditionType, Condition, Run
from rcdb.provider import RCDBProvider
from rcdb.log_format import BraceMessage as Lf
log = logging.getLogger('rcdb.coda_parser')         # create run configuration standard logger


def update_coda_conditions(context, parse_result):
    """
    Opens and parses coda file

    :return: None
    """

    # read xml file and get root and run-start element

    # Some assertions in the beginning
    assert isinstance(parse_result, CodaRunLogParseResult)
    assert isinstance(context, UpdateContext)
    assert isinstance(context.db, RCDBProvider)
    db = context.db

    # Run! Run Lu.. I mean, run number is the major thing, starting with it
    if parse_result.run_number is None:
        log.warn("parse_result.run_number is None. (!) Run. Number. Is. None!!!")
        return

    if context.reason == UpdateReasons.END and not db.get_run(parse_result.run_number):
        log.info(Lf("Run '{}' is not found in DB. But the update reason is end of run. "
                    "Considering there where no GO. Just prestart and Stop ", parse_result.run_number))
        return

    run = db.create_run(parse_result.run_number)


    # Run number

    # Run type condition
    db.add_condition(run, DefaultConditions.RUN_TYPE, xml_root.attrib["runtype"], True, auto_commit)

    # Session
    db.add_condition(run, DefaultConditions.SESSION, xml_root.attrib["session"], True, auto_commit)

    # Set the run as not properly finished (We hope that the next section will
    db.add_condition(run, DefaultConditions.IS_VALID_RUN_END, False, True, auto_commit)

    # Start time
    db.add_run_start_time(run, start_time)

    # First, we set update time as run end if we have End time we overwrite it
    db.add_run_end_time(run, update_time)

    # End time
    db.add_run_end_time(run, end_time)

    # Event number
    db.add_condition(run, DefaultConditions.EVENT_COUNT, event_count, True, auto_commit)

    # Components used
    db.add_condition(run, DefaultConditions.COMPONENTS, json.dumps(components), True, auto_commit)

    # RTVs
    db.add_condition(run, DefaultConditions.RTVS, json.dumps(rtvs), True, auto_commit)

    # Set the run as properly finished
    db.add_condition(run, DefaultConditions.IS_VALID_RUN_END, True, True, auto_commit)

    # Number of events
    db.add_condition(run, DefaultConditions.COMPONENTS, json.dumps(components), True, auto_commit)
    db.add_condition(run, DefaultConditions.COMPONENT_STATS, json.dumps(component_stats), True, auto_commit)


    db.add_condition(run, DefaultConditions.USER_COMMENT, user_comment, True, auto_commit)