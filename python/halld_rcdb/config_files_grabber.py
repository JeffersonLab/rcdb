from run_config_parser import ConfigFileParseResult, HallDMainConfigParseResult

import logging
import glob
import os

from rcdb.log_format import BraceMessage as F

# Setup logger
log = logging.getLogger('rcdb.halld.config_files_grabber')      # create run configuration standard logger


class HallDFilesGrabInfo(object):

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
        self.final_files = []
        self.com_files_by_roc = {}
        self.user_files_by_roc = {}

        if com_ver and com_dir:
            mask = self.MASK_FORMAT.format(name, com_ver)
            self.com_files_mask = os.path.join(self.com_dir, mask)
            self.com_files = glob.glob(self.com_files_mask)
            self.com_files_by_roc = self._map_by_roc(self.com_files)

        if user_ver and user_dir:
            mask = self.MASK_FORMAT.format(name, user_ver)
            self.user_files_mask = os.path.join(self.user_dir, mask)
            self.user_files = glob.glob(self.user_files_mask)
            self.user_files_by_roc = self._map_by_roc(self.user_files)

        for roc_name in self.com_files_by_roc.keys():
            if roc_name in self.user_files_by_roc:
                self.final_files.append(self.user_files_by_roc[roc_name])
            else:
                self.final_files.append(self.com_files_by_roc[roc_name])

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
        print("self.final_files = ", self.final_files)

    def _map_by_roc(self, file_paths):
        """
        Each file path contains rocfcal11_...., rocfcal12_... 
        This function create a map of like {"rocfcal11": <full_path>,  "rocfcal12": <full_path>}
                
        :param file_paths: array of paths to files
        :type file_paths: [str]
                 
        :return: 
        :rtype: {str:str}
        """
        result = {}
        for file_path in file_paths:
            base = os.path.basename(file_path)
            roc_name = base[:base.find('_')]
            result[roc_name] = file_path


def grab_additional_configuration_files(parse_result):
    assert (isinstance(parse_result, HallDMainConfigParseResult))

    # create list of file names
    if parse_result.bcal_fadc250_com_dir:
        fcal_info = HallDFilesGrabInfo('fcal',
                                       parse_result.st_fadc250_com_dir,
                                       parse_result.st_fadc250_com_ver,
                                       parse_result.st_fadc250_user_dir,
                                       parse_result.st_fadc250_user_ver)
        fcal_info.print_self()





