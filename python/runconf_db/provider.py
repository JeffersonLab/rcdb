"""@package AlchemyProvider
Documentation for this module.

More details.
"""

import re
import logging
from log_format import BraceMessage as Lf
import datetime

import sqlalchemy
from model import *

import posixpath
import file_archiver

log = logging.getLogger("rcdb.provider")


class ConfigurationProvider(object):
    """
    CCDB data provider that uses SQLAlchemy for accessing databases
    """

    def __init__(self):
        self._is_connected = False
        self._are_dirs_loaded = False
        self.path_name_regex = re.compile('^[\w\-_]+$', re.IGNORECASE)
        self._connection_string = ""
        self.logging_enabled = True
        self.engine = None


    #----------------------------------------------------------------------------------------
    #	C O N N E C T I O N
    #----------------------------------------------------------------------------------------


    #------------------------------------------------
    #  Connects to database using connection string
    #------------------------------------------------
    def connect(self, connection_string="mysql+mysqlconnector://runconf_db@127.0.0.1/runconf_db"):
        """
        Connects to database using connection string

        connection string might be in form:
        mysql://<username>:<password>@<mysql.address>:<port> <database>
        sqlite:///path/to/file.sqlite

        :param connection_string: connection string
        :type connection_string: str
        """

        try:
            self.engine = sqlalchemy.create_engine(connection_string)
        except ImportError, err:
            #sql alchemy uses MySQLdb by default. But it might be not install in the system
            #in such case we fallback to mysqlconnector which is embedded in CCDB
            if connection_string.startswith("mysql://") and "No module named MySQLdb" in repr(err):
                connection_string = connection_string.replace("mysql://", "mysql+mysqlconnector://")
                self.engine = sqlalchemy.create_engine(connection_string)
            else:
                raise

        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()
        self._is_connected = True
        self._connection_string = connection_string

        #since it is a new connection we need to rebuild directories
        self._are_dirs_loaded = False

    #------------------------------------------------
    # Closes connection to data
    #------------------------------------------------
    def disconnect(self):
        """Closes connection to database"""
        #TODO close pool logic???
        self._is_connected = False
        self.session.close()

    #-------------------------------------------------
    # indicates ether the connection is open or not
    #-------------------------------------------------
    @property
    def is_connected(self):
        """
        indicates ether the connection is open or not

        :return: bool True if connection is opened
        :rtype: bool
        """
        return self._is_connected

    #------------------------------------------------
    # Connection string that was used
    #------------------------------------------------
    @property
    def connection_string(self):
        """
        Connection string that was used on last connect()

        :return: connection string
        :rtype: str
        """
        return self._connection_string

    def obtain_board(self, board_type, serial):
        query = self.session.query(Board).filter(Board.board_type == board_type, Board.serial == serial)
        if not query.count():
            log.debug(Lf("Board type='{}' sn='{}' is not found in DB. Creating record", board_type, serial))
            board = Board()
            board.serial = serial
            board.board_type = board_type
            self.session.add(board)
            self.session.commit()
            log.info(Lf("Board type='{}' sn='{}' added to DB", board_type, serial))
            return board
        else:
            return query.first()

    def obtain_crate(self, name):
        """
        Gets or creates crate with the name
        """
        query = self.session.query(Crate).filter(Crate.name == name)
        if not query.count():
            log.debug(Lf("Crate '{}' is not found in DB. Creating record...", name))
            crate = Crate()
            crate.name = name
            self.session.add(crate)
            self.session.commit()
            log.info(Lf("Crate '{}' is added to DB", name))
            return crate
        else:
            return query.first()

    def obtain_board_installation(self, crate, board, slot):
        """
        Gets board installation by crate, board, slot. Create a new one in DB
        if there is no such installation
        """
        #some validation and value checks
        if isinstance(crate, basestring):
            crate = self.obtain_crate(crate)

        if isinstance(board, tuple):
            board_type, serial = board
            board = self.obtain_board(board_type, serial)
        assert isinstance(crate, Crate)
        assert isinstance(board, Board)
        slot = int(slot)

        query = self.session.query(BoardInstallation).filter(BoardInstallation.board_id == board.id,
                                                             BoardInstallation.crate_id == crate.id,
                                                             BoardInstallation.slot == slot)
        if not query.count():
            log.debug(Lf("Board installation for crate='{}', "
                         "board='{}', sn='{}', slot='{}' is not found in DB. Creating record...",
                         crate.name, board.board_type, board.serial, slot))
            installation = BoardInstallation()
            installation.board = board
            installation.crate = crate
            installation.slot = slot
            self.session.add(installation)
            self.session.commit()
            log.info(Lf("Board installation for crate='{}', "
                        "board='{}', sn='{}', slot='{}' added to DB",
                        crate.name, board.board_type, board.serial, slot))
            return installation
        else:
            return query.first()

    #------------------------------------------------
    # Gets directory by its full path
    #------------------------------------------------
    def obtain_run_configuration(self, run_num):
        """Gets or creates RunConfiguration for run"""
        query = self.session.query(RunConfiguration).filter(RunConfiguration.number == run_num)
        if not query.count():
            #no run configuration for this run is found
            run = RunConfiguration()
            run.number = run_num
            self.session.add(run)
            self.session.commit()
        else:
            run = query.first()

        assert isinstance(run, RunConfiguration)
        return run

    def obtain_dac_preset(self, board, values):
        """Gets or creates dac preset for board and dac values"""
        query = self.session.query(DacPreset) \
            .filter(DacPreset.board_id == board.id, DacPreset.text_values == list_to_db_text(values))
        if not query.count():
            preset = DacPreset()
            preset.board = board
            preset.values = values
            self.session.add(preset)
            self.session.commit()
        else:
            preset = query.first()

        assert isinstance(preset, DacPreset)
        return preset

    def add_board_config_to_run(self, run, board, dac_preset):
        """sets that the board have the dac preset values in the run"""
        if not isinstance(run, RunConfiguration):
            run = self.obtain_run_configuration(int(run))

        if not isinstance(dac_preset, DacPreset):
            dac_preset = self.obtain_dac_preset(board, dac_preset)

        #query = self.session.query(BoardConfiguration).join(BoardConfiguration.runs) \
        #    .filter(RunConfiguration.id == run.id,
        #            BoardConfiguration.board_id == board.id,
        #            BoardConfiguration.dac_preset_id == dac_preset.id)

        query = self.session.query(BoardConfiguration)\
                .filter(BoardConfiguration.board_id == board.id,
                        BoardConfiguration.dac_preset_id == dac_preset.id)

        #Get or create board configuration
        if not query.count():
            log.debug(Lf("Board configuration for board.id='{}', dac_preset.id='{}' not found",
                         board.id, dac_preset.id))
            board_config = BoardConfiguration()
            board_config.board = board
            board_config.dac_preset = dac_preset
            self.session.add(board_config)
            self.session.commit()
            log.info(Lf("Board configuration created for board.id='{}', dac_preset.id='{}'",
                        board.id, dac_preset.id))
        else:
            board_config = query.first()

        #check for run!
        if run not in board_config.runs:
            log.debug(Lf("Board configuration id='{}' not found in run='{}'", board_config.id, run.number))
            board_config.runs.append(run)
            self.session.commit()
            log.info(Lf("Board configuration id='{}' added to run='{}'", board_config.id, run.number))
        else:
            log.debug(Lf("Board configuration id='{}' is already in run='{}'", board_config.id, run.number))

    def add_board_installation_to_run(self, run, board_installation):
        """Adds board installation to run using crate, board, slot
        :run: run number or RunConfiguration object
        :board_installation: board installation object
        """
        if isinstance(board_installation, tuple):
            #it is (crate, board, slot)
            crate, board, slot = board_installation
            board_installation = self.obtain_board_installation(crate, board, slot)

        if not isinstance(run, RunConfiguration):
            run = self.obtain_run_configuration(int(run))
        assert isinstance(board_installation, BoardInstallation)

        if board_installation not in run.board_installations:
            log.debug(Lf("Board installation id='{}' is not associated with run='{}'",
                         board_installation.id, run.number))
            run.board_installations.append(board_installation)
            self.session.commit()
            log.info(Lf("Associated board_installation='{}' with run='{}'", board_installation.id, run.number))
        else:
            log.debug(Lf("Board installation id='{}' already associated with run='{}'",
                         board_installation.id, run.number))

    def add_run_start_time(self, run_num, dtm):
        """
            Sets staring time of run
            """
        assert (isinstance(dtm, datetime.datetime))

        log.debug(Lf("Setting start time '{}' to run '{}'", dtm, run_num))
        run = self.obtain_run_configuration(run_num)
        run.start_time = dtm
        self.session.commit()
        log.info(Lf("Start time changed to '{}' for run '{}'", dtm, run_num))


    def add_run_end_time(self, run_num, dtm):
        """Adds time of run"""
        assert (isinstance(dtm, datetime.datetime))

        log.debug(Lf("Setting end time '{}' to run '{}'", dtm, run_num))
        run = self.obtain_run_configuration(run_num)
        run.end_time = dtm
        self.session.commit()
        log.info(Lf("End time changed to '{}' for run '{}'", dtm, run_num))


    def add_run_record(self, run_number, key, value, actual_time=None, value_type="text"):
        """adds record for specified run"""
        if not actual_time is None:
            assert (isinstance(actual_time, datetime.datetime))

        run = self.obtain_run_configuration(run_number)

        #try to find such record in DB not to duplicate it
        query = self.session.query(RunRecord) \
            .filter(RunRecord.key == key,
                    RunRecord.value == value,
                    RunRecord.actual_time == actual_time,
                    RunRecord._run_conf_id == run.id)

        if query.count():
            log.debug(Lf("Run record key='{}', actual_time='{}' is already added to run='{}'",
                         key, actual_time, run.number))
            return  # such record already in database. Quit

        #Create a new record
        record = RunRecord()
        record.key = key
        record.value = value
        record.value_type = value_type
        record.actual_time = actual_time
        record.run = run

        #add record to DB
        self.session.add(record)
        self.session.commit()
        log.info(Lf("Added record of type '{}'", key))


    def add_configuration_file(self, run_num, path):
        """
                Adds configuration file to run configuration.
                If such file exists
            """
        log.debug("Processing configuration file")
        check_sum = file_archiver.get_file_sha256(path)
        run_conf = self.obtain_run_configuration(run_num)

        #Look, do we have such file?
        file_query = self.session.query(ConfigurationFile) \
            .filter(ConfigurationFile.sha256 == check_sum, ConfigurationFile.path == path)

        if not file_query.count():
            #no such file found!
            log.debug(Lf("|- File '{}' not found in DB", path))

            #create file.
            conf_file = ConfigurationFile()
            conf_file.sha256 = check_sum
            conf_file.path = path
            with open(path) as io_file:
                conf_file.content = io_file.read()

            #put it to DB and associate with run
            self.session.add(conf_file)
            self.session.commit()

            conf_file.runs.append(run_conf)

            #save and exit
            self.session.commit()
            log.info(Lf("File added to database. Path: '{}'. Run: '{}'", path, run_num))
            return

        #such file already exists! Get it from database
        conf_file = file_query.first()
        log.debug(Lf("|- File '{}' found in DB by id: '{}'", path, conf_file.id))

        #maybe... we even have this file in run conf?
        if conf_file not in run_conf.files:
            conf_file.runs.append(run_conf)
            #run_conf.files.append(conf_file)
            self.session.commit()  # save and exit
            log.info(Lf("File associated with run. Path: '{}'. Run: '{}'", path, run_num))
        else:
            log.debug(Lf("|- File already associated with run'{}'", run_num))
