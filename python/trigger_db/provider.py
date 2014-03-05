"""@package AlchemyProvider
Documentation for this module.

More details.
"""

import re
import logging
from log_format import BraceMessage as lf
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


#----------------------------------------------------------------------------------------
#	C O N N E C T I O N
#----------------------------------------------------------------------------------------


    #------------------------------------------------
    #  Connects to database using connection string
    #------------------------------------------------
    def connect(self, connection_string="mysql+mysqlconnector://trigger_db@127.0.0.1/trigger_db"):
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

    def add_run_start_time(self, run_num, dtm):
        """Sets staring time of run

        """
        assert (isinstance(dtm, datetime.datetime))

        log.debug(lf("Setting start time '{}' to run '{}'", dtm, run_num))
        run = self.obtain_run_configuration(run_num)
        run.start_time = dtm
        self.session.commit()
        log.info(lf("Start time changed to '{}' for run '{}'", dtm, run_num))

    def add_run_end_time(self, run_num, dtm):
        """Adds time of run"""
        assert (isinstance(dtm, datetime.datetime))

        log.debug(lf("Setting end time '{}' to run '{}'", dtm, run_num))
        run = self.obtain_run_configuration(run_num)
        run.end_time = dtm
        self.session.commit()
        log.info(lf("End time changed to '{}' for run '{}'", dtm, run_num))

    def add_run_record(self, run_number, record_type, data, actual_time=None, data_format="text"):
        """adds record for specified run"""
        if not actual_time is None:
            assert (isinstance(actual_time, datetime.datetime))

        run = self.obtain_run_configuration(run_number)

        #try to find such record in DB not to duplicate it
        query = self.session.query(RunRecord)\
            .filter(RunRecord.type == record_type,
                    RunRecord.data == data,
                    RunRecord.actual_time == actual_time,
                    RunRecord._run_conf_id == run.id)

        if query.count():
            return      # such record already there

        record = RunRecord()
        record.type = record_type
        record.data = data
        record.format = data_format
        record.actual_time = actual_time
        record.run = run

        self.session.add(record)
        self.session.commit()
        log.info(lf("Added record of type '{}'", record_type))

    def add_configuration_file(self, run_num, path):
        """
            Adds configuration file to run configuration.
            If such file exists
        """
        log.debug("Adding configuration file")
        check_sum = file_archiver.get_file_sha256(path)
        run_conf = self.obtain_run_configuration(run_num)

        #Look, do we have such file?
        file_query = self.session.query(ConfigurationFile)\
            .filter(ConfigurationFile.sha256 == check_sum, ConfigurationFile.path == path)

        if not file_query.count():
            #no such file found!
            log.debug(lf("|- File '{}' not found in DB", path))

            #create file.
            conf_file = ConfigurationFile()
            conf_file.sha256 = check_sum
            conf_file.path = path
            with open(path) as file:
                conf_file.content = file.read()

            #put it to DB and associate with run
            self.session.add(conf_file)
            self.session.commit()

            conf_file.runs.append(run_conf)

            #save and exit
            self.session.commit()
            log.info(lf("File added to database. Path: '{}'. Run: '{}'", path, run_num))
            return

        #such file already exists! Get it from database
        conf_file = file_query.first()
        log.debug(lf("|- File '{}' found in DB by id: '{}'", path, conf_file.id))

        #maybe... we even have this file in run conf?
        if conf_file not in run_conf.files:
            conf_file.runs.append(run_conf)
            #run_conf.files.append(conf_file)
            self.session.commit()   # save and exit
            log.info(lf("File associated with run. Path: '{}'. Run: '{}'", path, run_num))