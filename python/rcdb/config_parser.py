from ctypes import *
import os



MAX_FADC250_CH=16

class FADC250_CONF(Structure):
    """The original structure from confutils.h"""

    _fields_ = [("group", c_int),
                ("f_rev", c_int),
                ("b_rev", c_int),
                ("b_ID", c_int),
                ("SerNum", c_char*80),
                ("mode", c_int),
                ("winOffset", c_uint),
                ("winWidth", c_uint),
                ("nsb", c_uint),
                ("nsa", c_uint),
                ("npeak", c_uint),
                ("chDisMask", c_uint),
                ("trigMask", c_uint),
                ("thr", c_uint*MAX_FADC250_CH),
                ("dac", c_uint*MAX_FADC250_CH),
                ("ped", c_uint*MAX_FADC250_CH),
                ]


class ConfigParser(object):
    """
    Parses config files for FlashAdc250
    See src folder for example
    """

    def __init__(self):
        self.parser_lib = cdll.LoadLibrary(self._get_lib_full_path())
        self.parser_lib.getFadc250Config.restype = FADC250_CONF


    @staticmethod
    def _get_lib_full_path():
        if not "TDB_HOME" in os.environ:
            raise StandardError("TDB_HOME environment variable is not set but requred")

        home = os.environ["TDB_HOME"]
        return os.path.join(home, "src", "libconfutils.so")

    def parse_file(self, file_name):
        self.parser_lib.fadc250InitGlobals()
        c_name = c_char_p(file_name)

        self.parser_lib.fadc250ReadConfigFile(c_name)
        arr_len = self.parser_lib.getFadc250Length()
        print arr_len

        roc_name = string_at((c_char*255).in_dll(self.parser_lib, 'rocName'))

        print roc_name
        #if roc_name:
         #   print roc_name.value

        for i in range(arr_len):
            fadc250_conf = self.parser_lib.getFadc250Config(i)
            print("group {0}".format(fadc250_conf.group))
            print("SerNum {0}".format(fadc250_conf.SerNum))


if __name__ == "__main__":
    print("I'm here!")
    parser = ConfigParser()

    #compose path of sample file
    home = os.environ["TDB_HOME"]
    file_path = os.path.join(home, "src", "fadc250_example.cnf")

    #parse file
    parser.parse_file(file_path)





