import sys, os
import xml.etree.ElementTree as ET
import logging
from runconf_db.log_format import BraceMessage as lf
from runconf_db import ConfigurationProvider
from datetime import datetime

#setup logger
log = logging.getLogger('rcdb')                     # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))   # add console output for logger
log.setLevel(logging.DEBUG)                         # print everything. Change to logging.INFO for less output


#entry point
if __name__ == "__main__":

    #check we have arguments
    if len(sys.argv) < 2:
        print("Please provide a path to xml data file")
        sys.exit(1)

    #read xml file and get root element
    log.debug(lf("Parsing file {0}", sys.argv[1]))
    xml_root = ET.parse(sys.argv[1]).getroot()
    files = [xml_file.text for xml_file in xml_root.findall("file")]
    run_number = int(xml_root.find("run").attrib["number"])
    str_start_time = xml_root.find("run").find("start_time").text
    start_comment = xml_root.find("start_comment").text
    start_time = datetime.strptime(str_start_time,"%Y-%m-%d %H:%M:%S")

    #log gathered information
    log.info(lf("Files to add: '{}'","', '".join(files)))
    log.info(lf("Run_number '{}'",run_number))
    log.info(lf("Start time '{}'", start_time))
    log.info(lf("Start comment text: {}...", start_comment[0:100]))


    #add everything to run number

    db = ConfigurationProvider()
    db.connect()
    db.add_run_start_time(run_number, start_time)
    db.add_run_record(run_number, "Start comment", start_comment, start_time)
    db.add_configuration_file(run_number, sys.argv[1])
    for file in files:
        db.add_configuration_file(run_number, file)