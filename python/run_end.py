import sys, os
import xml.etree.ElementTree as ET
import logging
import runconf_db
from runconf_db.log_format import BraceMessage as lf
from runconf_db import ConfigurationProvider

from datetime import datetime

#setup logger
log = logging.getLogger('rcdb')                     # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))   # add console output for logger
log.setLevel(logging.DEBUG)                         # print everything. Change to logging.INFO for less output

def parse_end_run_data(filename):

    #read xml file and get root and run-start element
    log.debug(lf("Parsing end-run data from file {0}", filename))
    xml_root = ET.parse(filename).getroot()
    xml_run_end = xml_root.find("run-end")

    #read xml-root data (which is <coda runtype = "xxx" session = "yyy">
    runtype = xml_root.attrib["runtype"]
    session = xml_root.attrib["session"]
    run_number = int(xml_root.find("run-start").find("run-number").text)

    end_comment = xml_run_end.find("end-comment").text
    end_time = datetime.strptime(xml_run_end.find("end-time").text,"%Y-%m-%d %H:%M:%S")
    total_events = int(xml_run_end.find("total-evt").text)
    xml_components = xml_run_end.find("components").findall("component")
    statistics = []
    for xml_component in xml_components:
        name = xml_component.attrib["name"]
        comp_type = xml_component.attrib["type"]
        evt_rate = xml_component.find("evt-rate").text
        data_rate = xml_component.find("data-rate").text
        evt_number = xml_component.find("evt-number").text
        statistics.append((name, comp_type, evt_rate, data_rate, evt_number))

    #log gathered information
    log.info(lf("Run number '{}'", run_number))
    log.info(lf("End time '{}'", end_time))
    log.info(lf("End comment text: {}", (end_comment if len(end_comment) < 100 else end_comment[0:100] + "...")))

    #return run_number, end_time, end_comment, total_events
    #add everything to run number
    db = ConfigurationProvider()
    db.connect()
    db.add_run_end_time(run_number, end_time)
    db.add_run_record(run_number, runconf_db.END_COMMENT_RECORD_KEY, end_comment, end_time)
    db.add_configuration_file(run_number, filename)
    #db.add_run_statistics(run_number, total_events)
    for name, comp_type, evt_rate, data_rate, evt_number in statistics:
        db.add_run_component_statistics(run_number, end_time, name, comp_type, evt_rate, data_rate, evt_number)


#entry point
if __name__ == "__main__":

    #check we have arguments
    if len(sys.argv) < 2:
        print("Please provide a path to xml data file")
        sys.exit(1)

    file_name = sys.argv[1]
    parse_end_run_data(file_name)
