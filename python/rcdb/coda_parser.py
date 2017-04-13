import logging
import os
import xml.etree.ElementTree as Et
from datetime import datetime
from rcdb.log_format import BraceMessage as Lf

# Setup logger
log = logging.getLogger('rcdb.coda_parser')         # create run configuration standard logger
log.addHandler(logging.NullHandler())

# run config file name in rtvs collection
RUN_CONFIG_RTV = '%(config)'


class CodaRunLogParseResult(object):
    """ Class is responsible for holding data for daq update """

    def __init__(self):
        self.run_number = None           # The run number
        self.has_run_start = False       # File has <run-start> xml section
        self.has_run_end = False         # File has <run-end> xml section
        self.run_type = None             # the Run type. E.g. 'hd_all.tsg_cosmic'
        self.session = None              # Session E.g. 'hdops'
        self.start_time = None           # Time of the run start
        self.end_time = None             # Time of the run end
        self.update_time = None          # Time when the coda log file is written
        self.event_count = None          # The number of events in the run
        self.components = None           # a list of names of <components> section . E.g. ['ROCBCAL13', 'ROCFDC11', ...]
        self.component_stats = None      # dictionary with contents of the <components> section
        self.rtvs = None                 # dictionary with contents of <rtvs> section
        self.run_config_file = None      # config file with full path. E.g. /home/.../TRG_COSMIC_BCAL_raw_cdc_b1.conf
        self.run_config = None           # config file name. E.g. TRG_COSMIC_BCAL_raw_cdc_b1
        self.user_comment = None         # Daq comment by user
        self.evio_last_file = None       # Filename of the last evio file written by CODA ER
        self.evio_files_count = None     # The number of evio files written by CODA Event Recorder


def parse_file(filename):
    """
    Opens and parses coda file

    :return: context (it is filled after parsing the file)
    """

    # read xml file and get root and run-start element
    result = CodaRunLogParseResult()
    result.coda_log_file = filename
    log.debug(Lf("Parsing CODA file '{0}'", filename))
    xml_root = Et.parse(filename).getroot()
    return parse_xml(result, xml_root)


def parse_xml(parse_result, xml_root):
    """
    Parses ElementTree element that should contain whole coda file

    :param parse_result: CodaRunLogParseResult that holds all available update context
    :type parse_result: CodaRunLogParseResult

    :param xml_root: ElementTree parsed coda xml file
    :type xml_root: xml.etree.ElementTree

    :return: context
    """

    # read xml file and get root and run-start element
    log.debug("Processing xml tree ")

    # parse <run-start> section
    parse_start_run_data(parse_result, xml_root)

    # try parse run data
    parse_end_run_data(parse_result, xml_root)

    # try parse user comments
    parse_end_comment(parse_result, xml_root)

    return parse_result


def parse_start_run_data(parse_result, xml_root):
    """
    Parses ElementTree element that should contain whole coda file

    :param parse_result: CodaRunLogParseResult that holds all available update context
    :type parse_result: CodaRunLogParseResult

    :param xml_root: ElementTree parsed coda xml file
    :type xml_root: xml.etree.ElementTree

    :return: context
    """
    assert isinstance(parse_result, CodaRunLogParseResult)

    xml_run_start = xml_root.find("run-start")
    if xml_run_start is None:
        log.warning("No <run-start> section found!")
        return parse_result
    parse_result.has_run_start = True

    # Run number
    parse_result.run_number = int(xml_root.find("run-start").find("run-number").text)
    log.info(Lf("Run number '{}'", parse_result.run_number))

    # Run type condition
    parse_result.run_type = xml_root.attrib["runtype"]

    # Session
    parse_result.session = xml_root.attrib["session"]

    # Start time
    try:
        start_time = datetime.strptime(xml_run_start.find("start-time").text, "%m/%d/%y %H:%M:%S")
        parse_result.start_time = start_time
        log.info(Lf("Run start time is '{}'", start_time))
    except Exception as ex:
        log.warning("Error parsing <start-time> section: " + str(ex))

    # Update time
    try:
        update_time = datetime.strptime(xml_run_start.find("update-time").text, "%m/%d/%y %H:%M:%S")
        parse_result.update_time = update_time
        log.info(Lf("Update time is '{}'", update_time))
    except Exception as ex:
        log.warning("Error parsing <update-time> section: " + str(ex))

    # Event number
    xml_event_count = xml_run_start.find('total-evt')
    if xml_event_count is not None:
        parse_result.event_count = int(xml_event_count.text)

    # Components used
    xml_components = xml_run_start.find('components')
    parse_components(parse_result, xml_components)

    # RTVs
    xml_rtvs = xml_run_start.find('rtvs')
    if xml_rtvs is not None:
        rtvs = {rtv.attrib['name']: rtv.attrib['value'] for rtv in xml_rtvs.findall('rtv')}
        parse_result.rtvs = rtvs

        # run_config_file
        if RUN_CONFIG_RTV in rtvs.keys():
            parse_result.run_config_file = rtvs[RUN_CONFIG_RTV]
            parse_result.run_config = os.path.basename(parse_result.run_config_file)
            log.debug(Lf("Run config file extracted from rtvs '{}'", parse_result.run_config))

    return parse_result


def parse_end_run_data(parse_result, xml_root):
    """
    Parses coda file and adds end of run information to DB

    :param parse_result: CodaRunLogParseResult that holds all available update context
    :type parse_result: CodaRunLogParseResult

    :param xml_root: ElementTree parsed coda xml file
    :type xml_root: xml.etree.ElementTree

    :return: context

    """
    xml_run_end = xml_root.find("run-end")
    if xml_run_end is None:
        log.debug("No <run-end> section found in file")
        return parse_result
    parse_result.has_run_end = True

    # End time
    try:
        parse_result.end_time = datetime.strptime(xml_run_end.find("end-time").text, "%m/%d/%y %H:%M:%S")
    except Exception as ex:
        log.warning("Unable to parse <end-time> section in <run-end>. Error: " + str(ex))

    # Number of events
    parse_result.event_count = int(xml_run_end.find("total-evt").text)

    # Parse components
    xml_components = xml_run_end.find('components')
    parse_components(parse_result, xml_components)


def parse_components(parse_result, xml_components):
    """
        Parses <components> section fo coda log file

        :param parse_result: CodaRunLogParseResult that holds all available update context
        :type parse_result: CodaRunLogParseResult

        :param xml_components: ElementTree <components> section of xml file
        :type xml_components: xml.etree.ElementTree

        :return: context

        """

    if xml_components is not None:
        components = {}
        component_stats = {}
        for xml_component in xml_components.findall('component'):
            stats = {}

            def find_stat(name, cast):
                xml_field = xml_component.find(name)
                if xml_field is not None:
                    stats[name] = cast(xml_field.text)

            find_stat("evt-rate", float)  # <evt-rate>7.541666</evt-rate>
            find_stat("data-rate", float)  # <data-rate>19.369333333333334</data-rate>
            find_stat("evt-number", int)  # <evt-number>181</evt-number>
            find_stat("min-evt-size", float)  # <min-evt-size>0</min-evt-size>
            find_stat("max-evt-size", float)  # <max-evt-size>0</max-evt-size>
            find_stat("average-evt-size", float)  # <average-evt-size>0</average-evt-size>

            component_type = xml_component.attrib['type']
            components[xml_component.attrib['name']] = component_type
            component_stats[xml_component.attrib['name']] = stats

            if component_type == 'ER':
                last_file_xml = xml_component.find('out-file')
                if last_file_xml is not None and last_file_xml.text:
                    last_file = last_file_xml.text
                    # the last file is something like: hd_rawdata_011410_055.evio
                    u_pos = last_file.rfind('_')
                    d_pos = last_file.find('.')
                    # noinspection PyBroadException
                    try:
                        parse_result.evio_files_count = int(last_file[u_pos + 1:d_pos]) + 1
                    except:
                        log.warning(Lf("Can't parse file index for '{}' file", last_file))
                    parse_result.evio_last_file = last_file

        parse_result.components = components
        parse_result.component_stats = component_stats
    return parse_result


def parse_end_comment(parse_result, xml_root):
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

    :param parse_result: CodaRunLogParseResult that holds all available update context
    :type parse_result: CodaRunLogParseResult

    :param xml_root: ElementTree parsed coda xml file
    :type xml_root: xml.etree.ElementTree

    :return: context

    """
    # User comments
    xml_end_comment = xml_root.find("end-comment")
    if xml_end_comment is None:
        log.info("Unable to find <end-comment> section")
        return parse_result

    end_comment = xml_end_comment.text

    if "-------------" in end_comment:
        user_comment = end_comment[:end_comment.find("-------------")].strip()
        # "Add run comments here ...." - means user didn't add anything
        if user_comment == "Add run comments here ....":
            user_comment = ""
    else:
        log.warning(Lf("Log comment is in unknown format. "
                       "No '-----' separated part found. The comment is '{}'", end_comment))
        user_comment = end_comment

    parse_result.user_comment = user_comment
    return parse_result
