"""@package AlchemyProvider
Documentation for this module.

More details.
"""

import os
import re
import logging
import sys
from time import mktime
from collections.abc import MutableSequence

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError, NoResultFound

from ply.lex import LexToken

import sqlalchemy.orm
from sqlalchemy.orm import aliased
# from sqlalchemy.orm.exc import NoResultFound

import rcdb
import rcdb.file_archiver
from rcdb.alias import default_aliases
from rcdb.log_format import BraceMessage as Lf
from rcdb import lexer
from rcdb.stopwatch import StopWatchTimer
from rcdb.errors import OverrideConditionTypeError, NoConditionTypeFound, \
    NoRunFoundError, OverrideConditionValueError, QueryFormatError, QueryEvaluationError
from rcdb.model import *

log = logging.getLogger("rcdb.provider")

# Python 2 to 3 fix
if sys.version_info[0] == 3:
    # noinspection PyUnresolvedReferences
    basestring = str,


# noinspection PyTypeChecker
class RCDBProvider(object):
    """ RCDB data provider that uses SQLAlchemy for accessing databases """

    def __init__(self, connection_string=None, user_name="", check_version=True):
        self._is_connected = False
        self.path_name_regex = re.compile(r'^[\w\-_]+$', re.IGNORECASE)
        self._connection_string = ""
        self.logging_enabled = True
        self.engine = None
        self.session = None
        self._cnd_types_cache = None
        self._cnd_types_by_name = None
        self.aliases = default_aliases
        self._run_periods_cache = None

        # username for record
        self.user_name = user_name
        """:type: str"""
        if not user_name:
            if "RCDB_USER" in os.environ.keys():
                self.user_name = os.environ["RCDB_USER"]

        if connection_string:
            self.connect(connection_string, check_version)
        """:type : Session """

    # ------------------------------------------------
    # Check DB version
    # ------------------------------------------------
    def get_schema_version(self):
        """Check if connected SQL schema is of the right version"""

        schema_version, = self.session.query(SchemaVersion.version) \
            .order_by(desc(SchemaVersion.version)) \
            .first()

        return schema_version

    # ------------------------------------------------
    # Connects to database using connection string
    # ------------------------------------------------
    def connect(self, connection_string="mysql+pymysql://rcdb@127.0.0.1/rcdb", check_version=True):
        """
        Connects to database using connection string

        connection string might be in form:
        mysql://<username>:<password>@<mysql.address>:<port> <database>
        sqlite:///path/to/file.sqlite

        If check_version is FALSE, then the function doesn't check if database really has RCDB schema (tables).
        So if you need to connect to empty or old DB to create tables or update schema

        :param check_version: If False the database version is not checked a
        :param connection_string: connection string
        :type connection_string: str
        """

        if not connection_string:
            raise ValueError("Connection string is whitespace or empty. Provide proper connection string for DB")

        try:
            self.engine = sqlalchemy.create_engine(connection_string)
        except ImportError as err:
            # sql alchemy uses MySQLdb by default. But it might be not install in the system
            # in such case we fall back to mysqlconnector
            if connection_string.startswith("mysql://") and "No module named" in str(err) and 'MySQLdb' in str(err):
                connection_string = connection_string.replace("mysql://", "mysql+pymysql://")
                self.engine = sqlalchemy.create_engine(connection_string)
            else:
                raise

        session_type = sessionmaker(bind=self.engine)
        self.session = session_type()
        self._is_connected = True
        self._connection_string = connection_string

        if check_version:
            db_version = self.get_schema_version()
            if db_version != rcdb.SQL_SCHEMA_VERSION:
                message = "SQL schema version doesn't match. " \
                          "Retrieved DB version is {0}, required version is {1}" \
                    .format(db_version, rcdb.SQL_SCHEMA_VERSION)
                raise rcdb.errors.SqlSchemaVersionError(message)

    # ------------------------------------------------
    # Closes connection to data
    # ------------------------------------------------
    def disconnect(self):
        """Closes connection to database"""
        self._is_connected = False
        self.session.close()

    # -------------------------------------------------
    # indicates ether the connection is open or not
    # -------------------------------------------------
    @property
    def is_connected(self):
        """
        indicates ether the connection is open or not

        :return: bool True if connection is opened
        :rtype: bool
        """
        return self._is_connected

    # ------------------------------------------------
    # Connection string that was used
    # ------------------------------------------------
    @property
    def connection_string(self):
        """
        Connection string that was used on last connect()

        :return: connection string
        :rtype: str
        """
        return self._connection_string

    # -------------------------------------------------------------------
    # Adds log record to the database
    # -------------------------------------------------------------------
    def add_log_record(self, table_ids, description, related_run_number, do_commit=True):
        """
        Adds log record to the database
        :param table_ids: Str in form tablename_id, or list of such strings, or ModelBase object, or list[ModelBase]
        :type table_ids:str or list[str] or list[ModelBase] or Base or str

        :param description: Text description of what has been done
        :type description: str

        :param related_run_number: If it is possible a run number to which this record corresponds
        :type related_run_number: int

        :return:
        """

        if isinstance(related_run_number, Run):
            related_run_number = related_run_number.number

        record = LogRecord()

        # table ids?
        if isinstance(table_ids, Base):
            record.table_ids = table_ids.log_id
        elif isinstance(table_ids, list):
            if table_ids:
                if isinstance(table_ids[0], ModelBase):
                    record.table_ids = list_to_db_text([item.log_id for item in table_ids])
                elif isinstance(table_ids[0], str):
                    record.table_ids = list_to_db_text(table_ids)
        elif isinstance(table_ids, str):
            record.table_ids = table_ids

        # description
        record.description = str(description)
        record.related_run_number = related_run_number

        if self.user_name:
            record.user_name = self.user_name

        # save
        self.session.add(record)
        if do_commit:
            self.session.commit()
        log.info(description)

    # ------------------------------------------------
    # Gets Run or returns None
    # ------------------------------------------------
    def get_run(self, run_number):
        """Gets Run object from run_number
            :param run_number: the run number
            :param run_number: int

            :return: Run object corresponding to run number or None if there is no such run in DB
            :rtype: Run or None
        """
        if isinstance(run_number, Run):
            return run_number

        run_number = int(run_number)

        query = self.session.query(Run).filter(Run.number == run_number)
        return query.first()

    # ------------------------------------------------
    # Gets Runs in range [rum_min, run_max]
    # ------------------------------------------------
    def get_runs(self, rum_min, run_max, sort_desc=False):

        """ Gets all runs that rum_min<= run.number <= run_max

        :param sort_desc: If True result runs will be sorted by descending run-number
        :type run_max: int
        :type rum_min: int
        """
        query = self.session.query(Run).filter(Run.number >= rum_min, Run.number <= run_max)

        if sort_desc:
            query = query.order_by(Run.number.desc())
        else:
            query = query.order_by(Run.number)

        return query.all()

    # ------------------------------------------------
    # Gets Run or returns None
    # ------------------------------------------------
    def get_next_run(self, run_or_number):
        """Gets run which number is the next to given run_number
            :param run_or_number: the run number
            :param run_or_number: int, Run

            :return: Run object corresponding to run number or None if there is no such run in DB
            :rtype: Run or None
        """
        if isinstance(run_or_number, Run):
            run_number = run_or_number.number
        else:
            run_number = run_or_number

        query = self.session.query(Run).filter(Run.number > run_number).order_by(Run.number)
        return query.first()

    # ------------------------------------------------
    # Gets Run or returns None
    # ------------------------------------------------
    def get_prev_run(self, run_or_number):
        """Gets run which number is the previous to given run_number
            :param run_or_number: the run number
            :param run_or_number: int, Run

            :return: Run object corresponding to run number or None if there is no such run in DB
            :rtype: Run or None
        """
        if isinstance(run_or_number, Run):
            run_number = run_or_number.number
        else:
            run_number = run_or_number

        query = self.session.query(Run).filter(Run.number < run_number).order_by(Run.number.desc())
        return query.first()

    # ------------------------------------------------
    # Gets or creates Run
    # ------------------------------------------------
    def create_run(self, run_number):
        """Gets or creates Run with given number
            :type run_number: int
            :rtype: Run
        """
        run = self.get_run(run_number)
        if not run:
            # no run is found

            run = Run()
            run.number = run_number
            self.session.add(run)
            self.session.commit()

        return run

    # ------------------------------------------------
    # Returns run periods
    # ------------------------------------------------

    def get_run_periods(self):
        """Gets all run periods as a list of RunPeriod objects

        :return: all RunPeriods in db
        :rtype: list, [RunPeriod]
        """
        if self._run_periods_cache is not None:
            return self._run_periods_cache
        try:
            self._run_periods_cache = self.session.query(RunPeriod).all()
            return self._run_periods_cache
        except NoResultFound:
            return []

    # ------------------------------------------------
    # Creates run period
    # ------------------------------------------------
    def create_run_period(self, name, description, run_min, run_max, start_date, end_date):
        """
        Creates run period

        :param name: Short name or run period e.g. Gluex Spring 2018
        :type name: str

        :param description: More detailed description if needed
        :type description: str

        :return: ConditionType object that corresponds to created DB record
        :rtype: ConditionType
        """

        query = self.session.query(RunPeriod).filter(RunPeriod.run_min == run_min, RunPeriod.run_max == run_max)

        if query.count():
            # we've found a run period with this run_max and run_min
            rp = query.first()
            assert isinstance(rp, RunPeriod)

            message = f"Run period with run_min={run_min} and run_max={run_max} already exists in DB:" \
                      f"name={rp.name}, descr.={rp.description}, start_date={rp.start_date}, end_date={rp.end_date}"

            raise ValueError(message)
        else:
            # no such ConditionType found in the database
            rp = RunPeriod()
            rp.name = name
            rp.description = description
            rp.start_date = start_date
            rp.end_date = end_date
            rp.run_min = run_min
            rp.run_max = run_max

            try:
                self.session.add(rp)
                self.session.commit()
                # clear cache
                self._run_periods_cache = None
            except:
                self.session.rollback()
                raise

            log_desc = f"RunPeriod created with name='{name}', run_min='{run_min}' run_max='{run_max}'"
            self.add_log_record(rp, log_desc, 0)
            return rp

    # ------------------------------------------------
    # Returns condition type
    # ------------------------------------------------
    def get_condition_type(self, name):
        """Gets condition type by name

        :param name: name of condition
        :type name: str

        :return: ConditionType corresponding to name
        :rtype: ConditionType
        """
        if self._cnd_types_by_name:
            try:
                return self._cnd_types_by_name[name]
            except KeyError:
                pass
        try:
            return self.session.query(ConditionType).filter(ConditionType.name == name).one()
        except NoResultFound:
            message = "No ConditionType with name='{}' is found in DB".format(name)
            raise NoConditionTypeFound(message)

    # ------------------------------------------------
    # Returns condition type
    # ------------------------------------------------
    def get_condition_types_by_name(self):
        """Gets of all conditions types as dict where keys are names, and values are ConditionType-s

        :return: all ConditionTypes in db
        :rtype: dict, {ConditionType}
        """
        if self._cnd_types_by_name:
            return self._cnd_types_by_name

        types = self.get_condition_types()
        self._cnd_types_by_name = {t.name: t for t in types}
        return self._cnd_types_by_name

    # ------------------------------------------------
    # Returns condition type
    # ------------------------------------------------
    def get_condition_types(self):
        """Gets all condition types as a list of ConditionType objects

        :return: all ConditionTypes in db
        :rtype: list, [ConditionType]
        """
        if self._cnd_types_cache is not None:
            return self._cnd_types_cache
        try:
            self._cnd_types_cache = self.session.query(ConditionType).all()
            return self._cnd_types_cache
        except NoResultFound:
            return []

    # ------------------------------------------------
    # Creates condition type
    # ------------------------------------------------
    def create_condition_type(self, name, value_type, description):
        """
        Creates condition type

        :param name: name that is used to retrieve conditions
        :type name: str

        :param value_type: It is one of ConditionType.FI
        :type value_type: str

        :param description: Short description of the condition. 255 chars max
        :type description: str

        :return: ConditionType object that corresponds to created DB record
        :rtype: ConditionType
        """

        query = self.session.query(ConditionType).filter(ConditionType.name == name)

        if query.count():
            # we've found such type!
            ct = query.first()
            assert isinstance(ct, ConditionType)

            if ct.value_type != value_type:
                message = "Condition type with this name exists, but value type is different:" \
                          "Database value_type={}, new value_type={}".format(ct.value_type, value_type)

                raise OverrideConditionTypeError(message)

            if ct.description != description:
                message = "Condition type with this name exists, but description is different:" \
                          "Database description={}, new description={}".format(ct.description, description)

                raise OverrideConditionTypeError(message)

            # if we are here, selected ct is the same as requested
            return ct
        else:
            # no such ConditionType found in the database
            ct = ConditionType()
            ct.name = name
            ct.value_type = value_type
            ct.description = description
            try:
                self.session.add(ct)
                self.session.commit()
                # clear cache
                self._cnd_types_cache = None
                self._cnd_types_by_name = None
            except:
                self.session.rollback()
                raise

            self.add_log_record(ct, "ConditionType created with name='{}', type='{}'"
                                .format(name, value_type), 0)
            return ct

    # ------------------------------------------------
    # Adds condition value to database
    # ------------------------------------------------
    def add_condition(self, run, key, value, replace=False):
        result = self.add_conditions(run, [(key, value)], replace)
        if len(result):
            return result[0]

    # ------------------------------------------------
    # Adds condition value to database
    # ------------------------------------------------
    def add_conditions(self, run, key_values, replace=False):

        """ Adds many conditions values for the run

        Only one value is allowed for a run. If run already has this condition:
            1. It value is the same the func does nothing
            2. If value is different than in DB, function check 'replace' flag and do accordingly

        Example:
            db.add_condition(1, "event_count", 1000)                  # Ok. First addition to DB
            db.add_condition(1, "event_count", 1000)                  # Ok. Do nothing, such value already exists
            db.add_condition(1, "event_count", 2222)                  # Error. OverrideConditionValueError
            db.add_condition(1, "event_count", 2222, replace=True)    # Ok. Replacing existing value
            print(db.get_condition(1, "event_count"))
                value: 2222
                time:  None

        :param run: The run number for this condition value
        :type run: int, Run

        :param key_values: dict, list of lists or list of tuples:
                          {key: value}, [[key,value]], [(key, value)]

        :param replace: If true, function replaces existing value
        :type replace: bool

        :return: (add_list, update_list, ignore_list) - lists of what conditions had been added, updated or ignored
        :rtype: ([],[],[])
        """

        # 0. Run & Run number.
        if not isinstance(run, Run):  # run is given as run number not Run object
            run_number = run
            run = self.get_run(run_number)
        else:
            run_number = run.number

        if not run:
            message = "No run with run_number='{}' found".format(run_number)
            raise NoRunFoundError(message)

        # All condition types!
        ct_dict = self.get_condition_types_by_name()

        # 1.  Format key values. To be sure, they are in appropriate manner
        values_by_ct = {}  # values by condition type dict
        for row in key_values:
            # Is key_values dict or list?
            if isinstance(key_values, dict):
                key = row
                value = key_values[row]
            else:
                key, value = tuple(row)

            # get type
            if isinstance(key, ConditionType):
                ct = key
            else:
                assert isinstance(key, str)
                ct = ct_dict[key]

            if ct in values_by_ct:
                if ct.values_are_equal(value, values_by_ct[ct]):
                    continue

                message = "add_conditions key_values contains several different values for '{}' ".format(ct.name)
                raise KeyError(message)

            # validate value:
            value = ct.convert_value(value)
            values_by_ct[ct] = value

        # 2. Check which conditions are in the database
        add_list = []  # List of conditions to be added for the first time for the run
        ignore_list = []  # List of conditions that are exist and values are the same as DB
        update_list = []  # List of conditions that are exists for this run and need to be updated

        ids = [k.id for k in values_by_ct.keys()]
        db_conditions = self.session.query(Condition).join(ConditionType) \
            .filter(Condition.run_number == run_number) \
            .filter(Condition.condition_type_id.in_(ids)) \
            .all()

        # iterate over selected conditions
        for db_condition in db_conditions:
            assert isinstance(db_condition, Condition)
            value = values_by_ct[db_condition.type]

            # if value is float, use precision
            if db_condition.value_type == ConditionType.FLOAT_FIELD:
                # I'm sure the value is float here because of the validation above
                value_is_differ = abs(db_condition.value - value) >= 1e-12
            else:
                value_is_differ = db_condition.value != value

            if value_is_differ:
                update_list.append(db_condition.type)
            else:
                ignore_list.append(db_condition.type)

        for ct in values_by_ct.keys():
            if (ct not in update_list) and (ct not in ignore_list):
                add_list.append(ct)

        # Now we know what to do with all of the fields
        # >oO   Debug output
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            log.debug(Lf("add_conditions function pending actions: "))
            log.debug(Lf("('ignore' means value are the same as in db)"))
            for ct in values_by_ct.keys():
                if ct in update_list:
                    log.debug(Lf("   add    '{}'", ct.name))
                if ct in ignore_list:
                    log.debug(Lf("   ignore '{}'", ct.name))
                if ct in ignore_list:
                    log.debug(Lf("   update '{}'", ct.name))

        result = []
        # 3. Update conditions that should be updated
        if update_list:
            db_conditions_by_ct = {c.type: c for c in db_conditions}

            if not replace:
                ct = update_list[0]
                message = "Conditions {} already exists for the run_number='{}' " \
                          "but the values are different. DB saved value='{}', new value='{}'. " \
                          "(Add replace=True if you want to replace the old value)" \
                    .format(ct.name, run.number, db_conditions_by_ct[ct].value, values_by_ct[ct])
                raise OverrideConditionValueError(message)

            with self.session.no_autoflush:
                for ct in update_list:
                    db_condition = db_conditions_by_ct[ct]

                    # We have to replace the old value
                    db_condition.value = values_by_ct[ct]
                    db_condition.created = datetime.datetime.now()
                    result.append(db_condition)

        # 4. Add values
        with self.session.no_autoflush:
            for ct in add_list:
                # we haven't found the field in db, so add a new conditions
                condition = Condition()
                condition.type = ct
                condition.run = run
                condition.value = values_by_ct[ct]
                self.session.add(condition)
                result.append(condition)

        # 5. Commit changes
        self.session.commit()

        return result + ignore_list

    # ------------------------------------------------
    # Gets condition
    # ------------------------------------------------
    def get_condition(self, run_number, key):
        """ Returns condition value for the run
        If the is_many_per_run flag is allowed per condition, this function returns one of it
        get_condition_list returns multiple values

        :param run_number: the run number
        :type run_number: Run or int

        :param key: Condition name or ConditionType object
        :type key: str or ConditionType

        :return: Value or None if no such ConditionValue attached to the run
        :rtype: Condition
        """
        if isinstance(run_number, Run):
            run_number = run_number.number
        else:
            run_number = int(run_number)

        if isinstance(key, ConditionType):
            ct = key
        else:
            assert isinstance(key, str)
            ct = self.get_condition_type(key)

        query = self.session.query(Condition). \
            filter(Condition.type == ct, Condition.run_number == run_number)

        return query.first()

    # ------------------------------------------------
    # Gets file
    # ------------------------------------------------
    def get_file(self, run, file_path):
        """ Returns configuration file by run and file 

        :param file_path: file path as it was before DB
        
        :param run: the run number
        :type run: Run or int      

        :return: Value or None if no such ConditionValue attached to the run
        :rtype: ConfigurationFile
        """
        if not isinstance(run, Run):
            run = self.get_run(run)

        file_path = str(file_path)

        # noinspection PyUnresolvedReferences
        query = self.session.query(ConfigurationFile).join(ConfigurationFile.runs) \
            .filter(ConfigurationFile.runs.any(Run.number == run.number), ConfigurationFile.path == file_path)

        return query.first()

    """
    RCDB data provider that uses SQLAlchemy for accessing databases
    """

    # ------------------------------------------------
    # Adds start time
    # ------------------------------------------------
    def add_run_start_time(self, run, dtm):
        """
            Sets staring time of run
        """
        assert (isinstance(dtm, datetime.datetime))

        if not isinstance(run, Run):  # run is given as run number not Run object
            run = self.create_run(int(run))

        if run.start_time == dtm:
            return

        log.debug(Lf("Setting start time '{}' to run '{}'", dtm, run.number))

        run.start_time = dtm
        self.session.commit()

    # ------------------------------------------------
    # Adds end time
    # ------------------------------------------------
    def add_run_end_time(self, run, dtm):
        """Adds time of run"""
        assert (isinstance(dtm, datetime.datetime))

        if not isinstance(run, Run):  # run is given as run number not Run object
            run = self.create_run(int(run))

        if run.end_time == dtm:
            return

        log.debug(Lf("Setting end time '{}' to run '{}'", dtm, run.number))
        run.end_time = dtm
        self.session.commit()

    # ------------------------------------------------
    #
    # ------------------------------------------------
    def add_configuration_file(self, run, path, content=None, overwrite=False, importance=0):
        """Adds configuration file to run configuration. If such file exists
        :param importance: 0 - HIGH importance, 1 - LOWER importance. Is used to show in WEB interface
        :param overwrite: If this flag is true, such file for this run exists but checksumm is different,
                          file content will be overwritten
        :param content: Content of a file. If not given, func tryes to open file by path.
        :param path: Path of the file
        :param run: Run number
        """

        def get_content():
            if content:
                return content
            with open(path) as io_file:
                return io_file.read()

        log.debug("Processing configuration file")

        if content is None:
            log.debug(Lf("|- Content is not provided as func param, reading from FS '{}'", path))
            check_sum = rcdb.file_archiver.get_file_sha256(path)
        else:
            log.debug(Lf("|- Content is NOT none, using it to put to DB", path))
            check_sum = rcdb.file_archiver.get_string_sha256(content)

        if not isinstance(run, Run):  # run is given as run number not Run object
            run = self.create_run(run)

        if overwrite:
            # If we have to potentially overwrite the file, we have to apply another logic
            # First, we look at file with this name in this run
            query = self.session.query(ConfigurationFile) \
                .filter(ConfigurationFile.runs.contains(run)) \
                .filter(ConfigurationFile.path == path) \
                .order_by(desc(ConfigurationFile.id))  # we want latest
            if query.count():
                # There are file to overwrite!
                conf_file = query.first()
                conf_file.sha256 = check_sum
                conf_file.path = path
                conf_file.content = get_content()
                conf_file.importance = importance
                log.debug(Lf("|- File '{}' is getting overwritten", path))

                self.session.commit()
                return conf_file

        # Overwrite = false or is not possible
        # Look, do we have a file with such name and checksumm?
        file_query = self.session.query(ConfigurationFile) \
            .filter(ConfigurationFile.sha256 == check_sum, ConfigurationFile.path == path)

        if not file_query.count():
            # no such file found!
            log.debug(Lf("|- File '{}' not found in DB", path))

            # create file.
            conf_file = ConfigurationFile()
            conf_file.sha256 = check_sum
            conf_file.path = path
            conf_file.content = get_content()
            conf_file.importance = importance

            # put it to DB and associate with run
            self.session.add(conf_file)
            self.session.commit()

            conf_file.runs.append(run)

            # save and exit
            self.session.commit()
            self.add_log_record(conf_file, "File added to DB. Path: '{}'. Run: '{}'".format(path, run), run.number)
            return conf_file

        # such file already exists! Get it from database
        conf_file = file_query.first()
        log.debug(Lf("|- File '{}' found in DB by id: '{}'", path, conf_file.id))

        # maybe... we even have this file in run conf?
        if conf_file not in run.files:
            conf_file.runs.append(run)
            # run_conf.files.append(conf_file)
            self.session.commit()  # save and exit
            self.add_log_record(conf_file, "File associated. Path: '{}'. Run: '{}'".format(path, run), run.number)
        else:
            log.debug(Lf("|- File already associated with run'{}'", run))

        return conf_file


    def select_runs(self, search_str="", run_min=0, run_max=sys.maxsize, sort_desc=False):
        """ Obsolete. Searches RCDB for runs with e

        :param sort_desc: if True result runs will by sorted descendant by run_number, ascendant if False
        :param run_min: minimum run to search
        :param run_max: maximum run to search
        :param search_str: Search pattern
        :type search_str: str
        :return: List of runs matching criteria
        :rtype: RunSelectionResult
        """
        start_time_stamp = int(mktime(datetime.datetime.now().timetuple()) * 1000)
        preparation_sw = StopWatchTimer()

        if run_min > run_max:
            run_min, run_max = run_max, run_min

        # PHASE 0 - Maybe there is no query?!
        if not search_str or not search_str.strip():
            # If no query, just use get_runs function and return the result
            preparation_sw.stop()
            query_sw = StopWatchTimer()
            sel_runs = self.get_runs(run_min, run_max, sort_desc)
            query_sw.stop()

            result = RunSelectionResult(sel_runs, self)
            result.sort_desc = sort_desc
            result.filter_condition_names = []
            result.filter_condition_types = []
            result.performance["preparation"] = preparation_sw.elapsed
            result.performance["query"] = query_sw.elapsed
            result.performance["selection"] = 0
            result.performance["start_time_stamp"] = start_time_stamp

            return result

        # get all condition types
        all_cnt_types = self.get_condition_types()
        all_cnd_types_by_name = {cnd.name: cnd for cnd in all_cnt_types}
        all_cnd_names = [str(key) for key in all_cnd_types_by_name.keys()]

        # PHASE 1: getting what to search from search_str

        search_str = str(search_str)
        if '__' in search_str:
            raise QueryFormatError("Query contains restricted symbol: '__'")

        for alias in self.aliases:
            al_name = "@" + alias.name
            if al_name in search_str:
                search_str = search_str.replace(al_name, '(' + alias.expression + ')')

        search_str = search_str.replace('\n', ' ')
        search_str = search_str.replace('\r', ' ')

        tokens = [token for token in lexer.tokenize(search_str)]

        target_cnd_types = []
        names = []
        aliased_cnd_types = []
        aliased_cnd = []
        names_count = 0
        for token in tokens:
            if token.type in lexer.rcdb_query_restricted:
                raise QueryFormatError("Query contains restricted symbol: '{}'".format(token.value))

            if token.type != "NAME":
                continue

            if token.value == 'math':
                continue

            if token.value == 'startswith':
                continue

            if token.value not in all_cnd_names:
                message = "Name '{}' is not found in ConditionTypes".format(token.value)
                raise QueryFormatError(message)
            else:
                cnd_name = token.value
                cnd_type = all_cnd_types_by_name[token.value]
                target_cnd_types.append(cnd_type)

                token.value = "value[{}].value".format(names_count)
                names_count += 1

                names.append(cnd_name)
                aliased_cnd.append(aliased(Condition))
                aliased_cnd_types.append(aliased(ConditionType))

        # PHASE 2: Database query
        query = self.session.query()

        if not names_count:
            return None

        search_eval = " ".join([token.value for token in tokens if isinstance(token, LexToken)])

        for (i, alias_cnd) in enumerate(aliased_cnd):
            query = query.add_entity(alias_cnd).filter(alias_cnd.condition_type_id == target_cnd_types[i].id)
            if i != 0:
                query = query.filter(alias_cnd.run_number == aliased_cnd[0].run_number)

        query = query.filter(aliased_cnd[0].run_number >= run_min, aliased_cnd[0].run_number <= run_max) \
            .join(aliased_cnd[0].run)

        # apply sorting
        if not sort_desc:
            query = query.order_by(aliased_cnd[0].run_number)
        else:
            query = query.order_by(desc(aliased_cnd[0].run_number))

        preparation_sw.stop()
        query_sw = StopWatchTimer()

        values = query.all()

        query_sw.stop()

        selection_sw = StopWatchTimer()

        # PHASE 3: Selecting runs
        compiled_search_eval = compile(search_eval, '<string>', 'eval')

        sel_runs = []

        for value in values:
            if isinstance(value, Condition):
                value = (value,)
            run = value[0].run
            try:
                if eval(compiled_search_eval):
                    sel_runs.append(run)
            except Exception as ex:
                message = 'Error evaluating search query.\n' \
                          + '  Query: <<"{}">>, \n'.format(search_eval) \
                          + '  Names: {}, \n'.format(names) \
                          + '  Values: {} \n'.format(values) \
                          + '  Error ({}): {}'.format(type(ex), ex)
                raise QueryEvaluationError(msg=message)

        selection_sw.stop()
        result = RunSelectionResult(sel_runs, self)
        result.filter_condition_names = names
        result.filter_condition_types = target_cnd_types
        result.sort_desc = sort_desc
        result.performance["preparation"] = preparation_sw.elapsed
        result.performance["query"] = query_sw.elapsed
        result.performance["selection"] = selection_sw.elapsed
        result.performance["start_time_stamp"] = start_time_stamp

        return result

    def select_values(self, val_names=None, search_str="", run_min=0, run_max=sys.maxsize, sort_desc=False,
                      insert_run_number=True, runs=None):
        """ Searches RCDB for runs with e
        
        :param val_names: list of conditions names to select
        :param sort_desc: if True result runs will by sorted descendant by run_number, ascendant if False
        :param run_min: minimum run to search
        :param run_max: maximum run to search        
        :param runs: May be a list of runs to search from. In this case run_min and run_max are not used
        :param insert_run_number: If True the first column of the result will be a run number
        :param search_str: Search pattern
        :type search_str: str
        :return: List of runs matching criteria
        :rtype: RcdbSelectionResult
        """
        start_time_stamp = int(mktime(datetime.datetime.now().timetuple()) * 1000)
        total_sw = StopWatchTimer()
        preparation_sw = StopWatchTimer()

        if run_min > run_max:
            run_min, run_max = run_max, run_min

        # get all condition types
        all_cnd_types_by_name = self.get_condition_types_by_name()
        all_cnd_names = [str(key) for key in all_cnd_types_by_name.keys()]

        # PHASE 1: getting what to search from search_str

        search_str = str(search_str)
        if '__' in search_str:
            raise QueryFormatError("Query contains restricted symbol: '__'")

        for alias in self.aliases:
            al_name = "@" + alias.name
            if al_name in search_str:
                search_str = search_str.replace(al_name, '(' + alias.expression + ')')

        search_str = search_str.replace('\n', ' ')
        search_str = search_str.replace('\r', ' ')

        tokens = [token for token in lexer.tokenize(search_str)]

        target_cnd_types = []
        names = ["run"]
        for token in tokens:
            if token.type in lexer.rcdb_query_restricted:
                raise QueryFormatError("Query contains restricted symbol: '{}'".format(token.value))

            if token.type != "NAME":
                continue

            if token.value == 'math':
                continue

            if token.value == 'startswith':
                continue

            if token.value not in all_cnd_names:
                message = "Name '{}' is not found in ConditionTypes".format(token.value)
                raise QueryFormatError(message)
            else:
                cnd_name = token.value
                if cnd_name not in names:
                    cnd_type = all_cnd_types_by_name[token.value]
                    isinstance(cnd_type, ConditionType)

                    target_cnd_types.append(cnd_type)

                    token.value = "values[{}]".format(len(names))
                    names.append(cnd_name)
                else:
                    # we already has such name. We have to set token.value right
                    token.value = "values[{}]".format(names.index(cnd_name))  # +1 because run_num is alwais 0

        # result values table
        val_indexes = []

        # Check if val_names are given
        if not val_names:
            val_names = []

        for name in val_names:
            if name in names:
                val_indexes.append(names.index(name))
            else:
                cnd_type = all_cnd_types_by_name[name]
                target_cnd_types.append(cnd_type)
                val_indexes.append(len(names))
                names.append(name)

        # PHASE 2: Database query
        query = self.session.query()

        # do we have a list of runs?
        if runs:
            runs = [run.number if isinstance(run, Run) else int(run) for run in runs]
            where_clause = " WHERE runs.number in ({})".format(','.join([str(run) for run in runs]))
        else:
            where_clause = " WHERE runs.number >= :run_min AND runs.number <=:run_max"

        # build query
        query = "SELECT  runs.number run" + os.linesep
        query_joins = " FROM runs " + os.linesep
        for ct in target_cnd_types:
            assert isinstance(ct, ConditionType)
            table_name = ct.name + "_table"
            value_str = "  ,{}.{} {}{}".format(table_name, ct.get_value_field_name(), ct.name, os.linesep)
            if not value_str in query:
                query += value_str  # safe for duplicate entries which trigger DB errors

            # Now joins region
            join_str = "  LEFT JOIN conditions {0} " \
                       "  ON {0}.run_number = runs.number AND {0}.condition_type_id = {1}{2}" \
                .format(table_name, ct.id, os.linesep)

            if join_str not in query_joins:
                query_joins += join_str  # safe for duplicate entries which trigger DB errors

        mighty_query = query + os.linesep \
                       + query_joins + os.linesep \
                       + where_clause

        if not sort_desc:
            mighty_query = mighty_query + os.linesep + "ORDER BY runs.number"
        else:
            mighty_query = mighty_query + os.linesep + "ORDER BY runs.number DESC"

        preparation_sw.stop()
        query_sw = StopWatchTimer()

        sql = text(mighty_query)
        if runs:
            result = self.session.connection().execute(sql)  # runs are already in query
        else:

            #sql.bindparams(run_max=run_max, run_min=run_min)
            #result = self.session.connection().execute(sql)
            result = self.session.connection().execute(sql, {"run_min": run_min, "run_max":run_max})

        query_sw.stop()

        search_eval = " ".join([token.value for token in tokens if isinstance(token, LexToken)])

        selection_sw = StopWatchTimer()

        # PHASE 3: Selecting runs
        if search_eval:
            # did user set search string at all?
            compiled_search_eval = compile(search_eval, '<string>', 'eval')
        else:
            compiled_search_eval = None

        result_table = []

        for values in result:
            run = values[0]
            try:
                if not search_eval or eval(compiled_search_eval):
                    result_row = [run] if insert_run_number else []
                    for i in val_indexes:
                        val = values[i]
                        result_row.append(val)
                    result_table.append(result_row)
            except Exception as ex:
                # Condition value might be NoneType if it's not added to a run
                # TypeError arises when comparing none with value and it's OK
                if isinstance(ex, TypeError) and "NoneType" in str(ex):
                    continue

                message = 'Error evaluating search query.\n' \
                          + '  Query: <<"{}">>, \n'.format(search_eval) \
                          + '  Names: {}, \n'.format(names) \
                          + '  Values: {} \n'.format(values) \
                          + '  Error ({}): {}'.format(type(ex), ex)
                raise QueryEvaluationError(msg=message)

        selection_sw.stop()
        total_sw.stop()
        result = RcdbSelectionResult(result_table, self)
        result.filter_condition_names = names
        result.filter_condition_types = target_cnd_types
        result.sort_desc = sort_desc
        result.selected_conditions = ['run'] + val_names if insert_run_number else [] + val_names
        result.performance["preparation"] = preparation_sw.elapsed
        result.performance["query"] = query_sw.elapsed
        result.performance["selection"] = selection_sw.elapsed
        result.performance["start_time_stamp"] = start_time_stamp
        result.performance["total"] = total_sw.elapsed

        return result


class RcdbSelectionResult(MutableSequence):
    """Define a list format, which I can customize"""

    def __init__(self, rows=None, db=None):
        super(RcdbSelectionResult, self).__init__()
        self.filter_condition_types = []
        self.filter_condition_names = []
        self.selected_conditions = []
        self.db = db
        self.sort_desc = False

        js_now = int(mktime(datetime.datetime.now().timetuple()) * 1000)
        self.performance = {"preparation": 0,
                            "query": 0,
                            "selection": 0,
                            "start_time_stamp": js_now,
                            "get_conditions": 0,
                            "tabling_values": 0,
                            "total": 0
                            }

        if rows is not None:
            self.rows = list(rows)
        else:
            self.rows = list()

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, ii):
        return self.rows[ii]

    def __delitem__(self, ii):
        del self.rows[ii]

    def __setitem__(self, ii, val):
        self.rows[ii] = val
        return self.rows[ii]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return """<RCDBSelectionResult filer_cnd_names:{}, Runs:{}>""".format(self.filter_condition_names, self.rows)

    def insert(self, ii, val):
        self.rows.insert(ii, val)

    def append(self, val):
        list_idx = len(self.rows)
        self.insert(list_idx, val)


class RunSelectionResult(RcdbSelectionResult):
    """"""

    def __init__(self, runs=None, db=None):
        super(RunSelectionResult, self).__init__()
        self.filter_condition_types = []
        self.filter_condition_names = []
        self.selected_conditions = []
        self.db = db
        self.sort_desc = False

        js_now = int(mktime(datetime.datetime.now().timetuple()) * 1000)
        self.performance = {"preparation": 0,
                            "query": 0,
                            "selection": 0,
                            "start_time_stamp": js_now,
                            "get_conditions": 0,
                            "tabling_values": 0}

        if runs is not None:
            self.runs = list(runs)
        else:
            self.runs = list()

    def __len__(self):
        return len(self.runs)

    def __getitem__(self, ii):
        return self.runs[ii]

    def __delitem__(self, ii):
        del self.runs[ii]

    def __setitem__(self, ii, val):
        self.runs[ii] = val
        return self.runs[ii]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return """<RunSelectionResult filer_cnd_names:{}, Runs:{}>""".format(self.filter_condition_names, self.runs)

    def insert(self, ii, val):
        self.runs.insert(ii, val)

    def append(self, val):
        list_idx = len(self.runs)
        self.insert(list_idx, val)

    # noinspection PyUnresolvedReferences
    def get_values(self, condition_names, insert_run_number=False):

        if self.db is None or not self.runs:
            return [[]]

        # Condition names... are just one name?
        if isinstance(condition_names, basestring):
            condition_names = [condition_names]

        # No condition names?
        if not condition_names:
            if insert_run_number:
                return [[run.number] for run in self.runs]
            else:
                # noinspection PyUnusedLocal
                return [[] for run in self.runs]

        target_cnd_names = condition_names

        sw = StopWatchTimer()

        all_cnt_types = self.db.get_condition_types()
        all_cnd_types_by_name = {cnd.name: cnd for cnd in all_cnt_types}

        # getting target conditions types and sorting them by id
        target_cnd_types = [all_cnd_types_by_name[cnd_name] for cnd_name in target_cnd_names]
        ct_id_to_user_defined_order = {}
        for cnd_type in target_cnd_types:
            for i in range(0, len(condition_names)):
                if cnd_type.name == condition_names[i]:
                    ct_id_to_user_defined_order[cnd_type.id] = i
                    break

        target_cnd_types = sorted(target_cnd_types, key=lambda x: x.id)
        target_cnd_types_len = len(target_cnd_types)

        ids = [ct.id for ct in target_cnd_types]

        runs_asc = self.runs if not self.sort_desc else list(reversed(self.runs))

        run_numbers = [r.number for r in runs_asc]

        query = self.db.session.query(Condition) \
            .filter(Condition.condition_type_id.in_(ids), Condition.run_number.in_(run_numbers)) \
            .order_by(Condition.run_number, Condition.condition_type_id)

        conditions = query.all()

        # performance measurement
        sw.stop()
        self.performance["get_conditions"] = sw.elapsed
        sw = StopWatchTimer()

        # create empty rows
        rows = []

        def get_empty_row(run_number=0):
            """Creates empty rows properly
            :param run_number: run number to add
            """
            if insert_run_number:
                # noinspection PyTypeChecker
                return [run_number] + ([None] * target_cnd_types_len)
            else:
                return [None] * target_cnd_types_len

        type_index = 0
        prev_run = conditions[0].run_number

        row = get_empty_row(runs_asc[0].number)
        run_index = 0

        while runs_asc[run_index].number != prev_run:
            rows.append(row)
            run_index += 1
            row = get_empty_row(runs_asc[run_index].number)

        for condition in conditions:
            assert isinstance(condition, Condition)

            type_id = condition.condition_type_id
            if condition.run_number != prev_run:
                prev_run = condition.run_number

                while runs_asc[run_index].number != prev_run:
                    rows.append(row)
                    run_index += 1
                    row = get_empty_row(runs_asc[run_index].number)

                type_index = 0

            while type_index < target_cnd_types_len and type_id != target_cnd_types[type_index].id:
                type_index += 1
                if type_index == target_cnd_types_len:
                    type_index = 0

            cell_index = ct_id_to_user_defined_order[target_cnd_types[type_index].id]
            if insert_run_number:
                row[cell_index + 1] = condition.value
            else:
                row[cell_index] = condition.value

        # We have always have to
        rows.append(row)
        run_index += 1

        # It may happen that we run out of selected conditions, because condition is not set for all runs after
        # for example we have run=> condition   1=>x, 2=>y, 3=>None, 4=>None. DB will select only x and y conditions
        # and 2 rows [[1],[2]], while it should [[1],[2],[None],[None]]. So we have to put missing rows in the end
        while run_index < len(runs_asc):
            rows.append(get_empty_row(runs_asc[run_index].number))
            run_index += 1

        # performance measure
        sw.stop()
        self.performance["tabling_values"] = sw.elapsed

        if self.sort_desc:
            rows.reverse()
        return rows


class ConfigurationProvider(RCDBProvider):
    """Obsolete. Still exists for backward compatibility. All methods moved to RCDBProvider"""
    pass


def destroy_schema(db):
    assert isinstance(db, RCDBProvider)
    rcdb.model.Base.metadata.drop_all(db.engine)


def stamp_schema_version(db):
    """
    Stamp DB with current schema version.
    It is assumed that the function is used when schema is just created or updated from older version
    """

    db.session.query(SchemaVersion).delete()
    v = SchemaVersion()
    v.version = rcdb.SQL_SCHEMA_VERSION
    v.comment = "Schema V{} for RCDB>v0.9 (2023)".format(v.version)
    db.session.add(v)
    db.session.commit()
    return v


def destroy_all_create_schema(db):
    """
    Creates RCDB schema in database. Used for test purpuses
    :param db: RCDBProvider provider
    :return:
    """
    assert isinstance(db, RCDBProvider)
    try:
        destroy_schema(db)
    except OperationalError as ex:
        print("destroy_schema dropped OperationalError '{}' so it is considered that the database is empty".format(ex))

    rcdb.model.Base.metadata.create_all(db.engine)
    stamp_schema_version(db)


