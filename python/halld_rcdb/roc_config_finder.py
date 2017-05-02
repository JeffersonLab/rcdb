from run_config_parser import ConfigFileParseResult, HallDMainConfigParseResult

import logging
import glob
import os

from rcdb.log_format import BraceMessage as F

# Setup logger
log = logging.getLogger('rcdb.halld.config_files_grabber')      # create run configuration standard logger


class HallDFilesGrabInfo(object):
    """
        
    Sections of configuration file may contain information for per-ROC configurations files like this:
        ==========================
             FCAL   
        ==========================
        ...
        FADC250_COM_DIR      /gluex/CALIB/ALL/fadc250/default
        FADC250_COM_VER      default
        
        FADC250_USER_DIR     /gluonfs1/gluex/CALIB/FCAL/fadc250/user/spring_2017
        FADC250_USER_VER     ring2_hot_v2

    by default ROC configurations taken from COM_DIR using COM_VER to form name like rocbcal11_<COM_VER>.cnf
    but if USER_DIR and USER_VER is given, then the given files from USER_DIR are used instead of COM_DIR files
    
    This objects implements its logic and provides excessive information about ROC files
    """

    MASK_FORMAT = "roc{}*_{}.cnf"

    def __init__(self, name, files_tuple):
        """        
        :param name: Name like fcal, bcal, st... 
        :type name: str
        
        :type files_tuple: (str,str,str,str) 
        :param files_tuple: containing com_dir, com_ver, user_dir, user_ver (in that order)
                           sections from config file
        """
        com_dir, com_ver, user_dir, user_ver = files_tuple
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
        log.debug("self.name = ", self.name)
        log.debug("self.com_dir = ", self.com_dir)
        log.debug("self.com_ver = ", self.com_ver)
        log.debug("self.user_dir = ", self.user_dir)
        log.debug("self.user_ver = ", self.user_ver)
        log.debug("self.com_files_mask = ", self.com_files_mask)
        log.debug("self.user_files_mask = ", self.user_files_mask)

        log.debug("self.com_files:")
        for file_name in self.com_files:
            log.debug("   {}".format(file_name))

        log.debug("self.user_files:")
        for file_name in self.user_files:
            log.debug("   {}".format(file_name))

        log.debug("self.final_files:")
        for file_name in self.final_files:
            log.debug("   {}".format(file_name))

    def _map_by_roc(self, file_paths):
        """
        Each file path contains rocfcal11_...., rocfcal12_...
        This function create a map of like {"rocfcal11": <full_path>,  "rocfcal12": <full_path>}

        :param file_paths: array of paths to files
        :type file_paths: [str]

        :return:
        :rtype: dict[str,str]
        """
        result = {}
        for file_path in file_paths:
            base = os.path.basename(file_path)
            roc_name = base[:base.find('_')]
            result[roc_name] = file_path
        return result


def find_roc_configuration_files(parse_result):
    """
    Gets HallDFilesGrabInfo files for standard sections    
    
    :param parse_result: 
    :return: List of HallDFilesGrabInfo objects for different sections
    :rtype: list[HallDFilesGrabInfo]
    """
    assert (isinstance(parse_result, HallDMainConfigParseResult))

    infos = []

    # create list of file names
    if parse_result.fcal_fadc250_files_info:
        infos.append(HallDFilesGrabInfo('fcal', parse_result.fcal_fadc250_files_info))

    if parse_result.bcal_fadc250_files_info:
        infos.append(HallDFilesGrabInfo('bcal', parse_result.bcal_fadc250_files_info))

    if parse_result.tof_fadc250_files_info:
        infos.append(HallDFilesGrabInfo('tof', parse_result.tof_fadc250_files_info))

    if parse_result.tagh_fadc250_files_info:
        infos.append(HallDFilesGrabInfo('tagh', parse_result.tagh_fadc250_files_info))

    if parse_result.st_fadc250_files_info:
        infos.append(HallDFilesGrabInfo('st', parse_result.st_fadc250_files_info))

    return infos


