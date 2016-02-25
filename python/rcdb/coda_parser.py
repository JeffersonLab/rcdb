import sys
import os
import xml.etree.ElementTree as ET
import logging
import rcdb
import json
from rcdb import DefaultConditions
from rcdb.model import ConditionType
from rcdb.log_format import BraceMessage as lf
from rcdb import ConfigurationProvider
from rcdb import create_condition_types


from datetime import datetime

# Setup logger
log = logging.getLogger('rcdb.coda_parser')         # create run configuration standard logger


# run config file name in rtvs collection
RUN_CONFIG_RTV = '%(config)'


class CodaConfigParseResult:
    def __init__(self):
        self.db = None
        self.run = -1
        self.has_run_start = False
        self.has_run_end = False


def parse_file(db, filename, auto_commit=True):
    """
    Opens and parses coda file

    :param db: Database object with functions that add data
    :type db: ConfigurationProvider

    :param filename: Path to the file
    :type filename: str

    :return: None
    """

    # read xml file and get root and run-start element
    log.debug(lf("Parsing CODA file '{0}'", filename))
    xml_root = ET.parse(filename).getroot()
    return parse_xml(db, xml_root, auto_commit)


def parse_xml(db, xml_root, auto_commit=True):
    """
    Parses ElementTree element that should contain whole coda file

    :param db: Database object with functions that add data
    :type db: ConfigurationProvider

    :param xml_root: ElementTree parsed coda xml file
    :type xml_root: xml.etree.ElementTree

    :return: None
    """

    # read xml file and get root and run-start element
    log.debug("Processing xml tree ")

    # Check that all condition types exists in DB
    create_condition_types(db)

    # parse <run-start> section
    run, run_config_file = parse_start_run_data(db, xml_root)

    # try parse run data
    parse_end_run_data(db, run, xml_root)

    # try parse user comments
    parse_end_comment(db, run, xml_root)

    return run, run_config_file


def parse_start_run_data(db, xml_root, auto_commit=True):
    """
    Parses ElementTree element that should contain whole coda file

    :param db: Database object with functions that add data
    :type db: ConfigurationProvider

    :param xml_root: ElementTree parsed coda xml file
    :type xml_root: xml.etree.ElementTree

    :return: None
    """

    xml_run_start = xml_root.find("run-start")
    if xml_run_start is None:
        log.warning("No <run-start> section found!")
        return None, ""

    # Run number
    run = db.create_run(int(xml_root.find("run-start").find("run-number").text))
    log.info(lf("Run number '{}'", run.number))

    # Run type condition
    db.add_condition(run, DefaultConditions.RUN_TYPE, xml_root.attrib["runtype"], True, auto_commit)

    # Session
    db.add_condition(run, DefaultConditions.SESSION, xml_root.attrib["session"], True, auto_commit)

    # Set the run as not properly finished (We hope that the next section will
    db.add_condition(run, DefaultConditions.IS_VALID_RUN_END, False, True, auto_commit)

    # Start time
    try:
        start_time = datetime.strptime(xml_run_start.find("start-time").text,"%m/%d/%y %H:%M:%S")
        db.add_run_start_time(run, start_time)
        log.info(lf("Run start time is '{}'", start_time))
    except Exception as ex:
        log.warning("Error parsing <start-time> section: " + str(ex))

    # Update time
    try:
        update_time = datetime.strptime(xml_run_start.find("update-time").text,"%m/%d/%y %H:%M:%S")
        db.add_run_end_time(run, update_time)
        log.info(lf("Update time is '{}'", update_time))
    except Exception as ex:
        log.warning("Error parsing <update-time> section: " + str(ex))

    # Event number
    xml_event_count = xml_run_start.find('total-evt')
    if xml_event_count is not None:
        event_count = int(xml_event_count.text)
        db.add_condition(run, DefaultConditions.EVENT_COUNT, event_count, True, auto_commit)

    # Components used
    xml_components = xml_run_start.find('components')
    if xml_components is not None:
        components = {comp.attrib['name']: comp.attrib['type'] for comp in xml_components.findall('component')}
        db.add_condition(run, DefaultConditions.COMPONENTS, json.dumps(components), True, auto_commit)

    # RTVs
    run_config_file = ""
    xml_rtvs = xml_run_start.find('rtvs')
    if xml_rtvs is not None:
        rtvs = {rtv.attrib['name']: rtv.attrib['value'] for rtv in xml_rtvs.findall('rtv')}
        db.add_condition(run, DefaultConditions.RTVS, json.dumps(rtvs), True, auto_commit)

        # run_config_file
        if RUN_CONFIG_RTV in rtvs.keys():
            run_config_file = rtvs[RUN_CONFIG_RTV]
            run_config = os.path.basename(run_config_file)
            db.add_condition(run, DefaultConditions.RUN_CONFIG, run_config, True, auto_commit)
            log.debug(lf("Run config file extracted from rtvs '{}'", run_config))

    return run, run_config_file


def parse_end_run_data(db, run, xml_root, auto_commit=True):
    """
    Parses coda file and adds end of run information to DB

    :param db: Database object with functions that add data
    :type db: ConfigurationProvider

    :param xml_root: ElementTree parsed coda xml file
    :type xml_root: xml.etree.ElementTree

    :param auto_commit: If true each change is committed to DB on each operation

    :return: None

    """
    xml_run_end = xml_root.find("run-end")
    if xml_run_end is None:
        log.debug("No <run-end> section found in file")
        return

    # End time
    try:
        end_time = datetime.strptime(xml_run_end.find("end-time").text, "%m/%d/%y %H:%M:%S")
    except Exception as ex:
        log.warning("Unable to parse <end-time> section in <run-end>. Error: " + str(ex))
        log.warning("Using datetime.now() to recover")
        end_time = datetime.now()

    db.add_run_end_time(run, end_time)



    # Set the run as properly finished
    db.add_condition(run, DefaultConditions.IS_VALID_RUN_END, True, None, True, auto_commit)

    # Number of events
    event_count = int(xml_run_end.find("total-evt").text)
    db.add_condition(run, DefaultConditions.EVENT_COUNT, event_count, None, True, auto_commit)

    # Components used
    xml_components = xml_run_end.find('components')
    if xml_components is not None:
        components = {}
        component_stats = {}
        for xml_component in xml_components.findall('component'):
            stats = {}

            def find_stat(name, cast):
                xml_field = xml_component.find(name)
                if xml_field is not None:
                    stats[name] = cast(xml_field.text)

            find_stat("evt-rate", float)            # <evt-rate>7.541666</evt-rate>
            find_stat("data-rate", float)           # <data-rate>19.369333333333334</data-rate>
            find_stat("evt-number", int)            # <evt-number>181</evt-number>
            find_stat("min-evt-size", float)        # <min-evt-size>0</min-evt-size>
            find_stat("max-evt-size", float)        # <max-evt-size>0</max-evt-size>
            find_stat("average-evt-size", float)    # <average-evt-size>0</average-evt-size>

            components[xml_component.attrib['name']] = xml_component.attrib['type']
            component_stats[xml_component.attrib['name']] = stats

        db.add_condition(run, DefaultConditions.COMPONENTS, json.dumps(components), None, True, auto_commit)
        db.add_condition(run, DefaultConditions.COMPONENT_STATS, json.dumps(component_stats), None, True, auto_commit)


def parse_end_comment(db, run, xml_root, auto_commit=True):
    """ Parses end comment

    It is assumed that the comment is in form:
    <end-comment>
    Add run comments here ....

    -------------------------------------------
    Date        : Mon Feb 16 16:53:09 EST 2015
    RUN_NUMBER  : 002472 (2472)
    RUN TYPE    : hd_bcal_n.ti
    RUN CONFIG  : led_upstream_mode8.cnf
    RAID DIR    :
    -------------------------------------------
    </end-comment>


    :return: user_comment, run_type_file, run_config
    :rtype: (str,str,str)
    """
    # User comments
    xml_end_comment = xml_root.find("end-comment")
    if xml_end_comment is None:
        log.info("Unable to find <end-comment> section")
        return

    end_comment = xml_end_comment.text

    if "-------------" in end_comment:
        user_comment = end_comment[:end_comment.find("-------------")].strip()
        # "Add run comments here ...." - means user didn't add anything
        if user_comment == "Add run comments here ....":
            user_comment = ""
    else:
        log.warning(lf("Log comment is in unknown format. "
                       "No '-----' separated part found. The comment is '{}'", end_comment))
        user_comment = end_comment

    db.add_condition(run, DefaultConditions.USER_COMMENT, user_comment, None, True, auto_commit)



