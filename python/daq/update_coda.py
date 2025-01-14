import json
import logging

from rcdb import UpdateContext, UpdateReasons, DefaultConditions
from rcdb.coda_parser import CodaRunLogParseResult
from rcdb.log_format import BraceMessage as Lf
from rcdb.provider import RCDBProvider


# Setup logger
log = logging.getLogger('rcdb.update_coda')         # create run configuration standard logger


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
        log.warning("parse_result.run_number is None. (!) Run. Number. Is. None!!!")
        return

    if context.reason == UpdateReasons.END and not db.get_run(parse_result.run_number):
        log.info(Lf("Run '{}' is not found in DB. But the update reason is end of run. "
                    "Considering there where no GO. Only prestart and then Stop ", parse_result.run_number))
        return

    run = db.create_run(parse_result.run_number)

    conditions = []

    # Run type condition
    if parse_result.run_type is not None:
        log.info(f" |- {DefaultConditions.RUN_TYPE:<17} : {parse_result.run_type}")
        conditions.append((DefaultConditions.RUN_TYPE, parse_result.run_type))

    # Session (like hdops)
    if parse_result.session is not None:
        log.info(f" |- {DefaultConditions.SESSION:<17} : {parse_result.session}")
        conditions.append((DefaultConditions.SESSION, parse_result.session))

    # Set the run as not properly finished (We hope that the next section will
    if parse_result.has_run_end is not None:
        log.info(f" |- {DefaultConditions.IS_VALID_RUN_END:<17} : {parse_result.has_run_end}")
        conditions.append((DefaultConditions.IS_VALID_RUN_END, parse_result.has_run_end))

    # The number of events in the run
    if parse_result.event_count is not None:
        log.info(f" |- {DefaultConditions.EVENT_COUNT:<17} : {parse_result.event_count}")
        conditions.append((DefaultConditions.EVENT_COUNT, parse_result.event_count))

    # a list of names of <components> section . E.g. ['ROCBCAL13', 'ROCFDC11', ...]
    if parse_result.components is not None:
        conditions.append((DefaultConditions.COMPONENTS, json.dumps(parse_result.components)))

    # dictionary with contents of the <components> section
    if parse_result.component_stats is not None:
        conditions.append((DefaultConditions.COMPONENT_STATS, json.dumps(parse_result.component_stats)))

    # RTVs
    if parse_result.rtvs is not None:
        conditions.append((DefaultConditions.RTVS, json.dumps(parse_result.rtvs)))

    # Daq comment by user
    if parse_result.user_comment is not None:
        conditions.append((DefaultConditions.USER_COMMENT, parse_result.user_comment))

    # config file name. E.g. TRG_COSMIC_BCAL_raw_cdc_b1
    if parse_result.run_config is not None:
        conditions.append((DefaultConditions.RUN_CONFIG, parse_result.run_config))

    # Filename of the last evio file written by CODA ER
    if parse_result.evio_last_file is not None:
        log.info(f" |- evio_last_file    : {parse_result.evio_last_file}")
        conditions.append(('evio_last_file', parse_result.evio_last_file))

    # The number of evio files written by CODA Event Recorder
    if parse_result.evio_files_count is not None:
        log.info(f" |- evio_files_count  : {parse_result.evio_files_count}")
        conditions.append(('evio_files_count', parse_result.evio_files_count))

    # SAVE CONDITIONS
    db.add_conditions(run, conditions, replace=True)

    log.info(Lf("update_coda: Saved {} conditions to DB", len(conditions)))

    # Start and end times
    if parse_result.start_time is not None:
        run.start_time = parse_result.start_time     # Time of the run start
        log.info(Lf("Run start time is {}", parse_result.start_time))

    if parse_result.end_time is not None:
        run.end_time = parse_result.end_time         # Time of the run end
        log.info(Lf("Run end time is {}. Set from end_time record", parse_result.end_time))
    else:
        if parse_result.update_time is not None:
            run.end_time = parse_result.update_time  # Fallback, set time when the coda log file is written as end time
            log.info(Lf("Run end time is {}. Set from update_time record", parse_result.update_time))

    db.session.commit()     # Save run times
