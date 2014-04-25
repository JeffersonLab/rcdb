import sys, os
import xml.etree.ElementTree as ET
import logging
import rcdb
from rcdb.log_format import BraceMessage as lf
from rcdb import ConfigurationProvider

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

    #read xml file and get root and run-start element
    log.debug(lf("Parsing file {0}", sys.argv[1]))
    xml_root = ET.parse(sys.argv[1]).getroot()
    xml_run_start = xml_root.find("run-start")

    #read xml-root data (which is <coda runtype = "xxx" session = "yyy">
    runtype = xml_root.attrib["runtype"]
    session = xml_root.attrib["session"]

    #read run-start info
    files = [xml_file.text for xml_file in xml_run_start.findall("file")]
    run_number = int(xml_run_start.find("run-number").text)

    xml_start_comment = xml_run_start.find("start-comment")
    start_comment = xml_start_comment.text if xml_start_comment else None   # start comment could be absent

    start_time = datetime.strptime(xml_run_start.find("start-time").text,"%Y-%m-%d %H:%M:%S")

    #log gathered information
    log.info(lf("Files to add: '{}'","', '".join(files)))
    log.info(lf("Run_number '{}'", run_number))
    log.info(lf("Start time '{}'", start_time))
    log.info(lf("Start comment text: {}...", start_comment[0:100] if start_comment else None))

    #add everything to run number
    db = ConfigurationProvider()
    db.connect()
    db.add_run_start_time(run_number, start_time)
    if start_comment:
        db.add_run_record(run_number, rcdb.START_COMMENT_RECORD_KEY, start_comment, start_time)
    db.add_configuration_file(run_number, sys.argv[1])
    for file in files:
        db.add_configuration_file(run_number, os.path.abspath(file))