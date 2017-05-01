from run_config_parser import ConfigFileParseResult, HallDMainConfigParseResult

import logging
import glob
import os

from rcdb.log_format import BraceMessage as F

# Setup logger
log = logging.getLogger('rcdb.halld.config_files_grabber')      # create run configuration standard logger


class ConfigurationFileInfo(object):

    MASK_FORMAT = "roc{}*_{}.cnf"

    def __init__(self, name, com_dir, com_ver, user_dir, user_ver):
        self.name = name
        self.com_dir = com_dir
        self.com_ver = com_ver
        self.user_dir = user_dir
        self.user_ver = user_ver
        self.com_files_mask = None
        self.user_files_mask = None
        self.com_files = []
        self.user_files = []

        if com_ver and com_dir:
            mask = self.MASK_FORMAT.format(name, com_ver)
            self.com_files_mask = os.path.join(self.com_dir, mask)
            self.com_files = glob.glob(self.com_files_mask)

        if user_ver and user_dir:
            mask = self.MASK_FORMAT.format(name, user_ver)
            self.user_files_mask = os.path.join(self.user_dir, mask)
            self.user_files = glob.glob(self.user_files_mask)

    def print_self(self):
        print("self.name = ", self.name)
        print("self.com_dir = ", self.com_dir)
        print("self.com_ver = ", self.com_ver)
        print("self.user_dir = ", self.user_dir)
        print("self.user_ver = ", self.user_ver)
        print("self.com_files_mask = ", self.com_files_mask)
        print("self.user_files_mask = ", self.user_files_mask)
        print("self.com_files  = ", self.com_files)
        print("self.user_files  = ", self.user_files)

    def _map_by_roc(self, file_pathes):
        result = {}
        for file_path in file_pathes:
            os.path.basename(file_path)




def grab_additional_configuration_files(parse_result):
    assert (isinstance(parse_result, HallDMainConfigParseResult))

    # create list of file names
    if parse_result.bcal_fadc250_com_dir:
        bcal_info = ConfigurationFileInfo('bcal',
                                          parse_result.st_fadc250_com_dir,
                                          parse_result.st_fadc250_com_ver,
                                          parse_result.st_fadc250_user_dir,
                                          parse_result.st_fadc250_user_ver)
        bcal_info.print_self()





