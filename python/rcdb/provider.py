"""@package AlchemyProvider
Documentation for this module.

More details.
"""
import os

import re
import logging
import sys
from collections import MutableSequence
from time import mktime

import rcdb
from rcdb.alias import default_aliases

from ply.lex import LexToken

from log_format import BraceMessage as Lf
from rcdb import lexer
from rcdb.stopwatch import StopWatchTimer
from sqlalchemy.exc import OperationalError
from .errors import OverrideConditionTypeError, NoConditionTypeFound, NoRunFoundError, OverrideConditionValueError, \
    QueryFormatError
import sqlalchemy.orm
from sqlalchemy.orm import joinedload, aliased

from model import *

import file_archiver
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger("rcdb.provider")


class RCDBProvider(object):
    """ RCDB data provider that uses SQLAlchemy for accessing databases """

    def __init__(self, connection_string=None, user_name="", check_version=True):
        self._is_connected = False
        self.path_name_regex = re.compile('^[\w\-_]+$', re.IGNORECASE)
        self._connection_string = ""
        self.logging_enabled = True
        self.engine = None
        self.session = None
        self._cnd_types_cache = None
        self._cnd_types_by_name = None
        self.aliases = default_aliases

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
    def is_acceptable_sql_version(self):
        """Check if connected SQL schema is of the right version"""
        try:
            return bool(self.session.query(func.count(SchemaVersion.version))
                        .filter(SchemaVersion.version == rcdb.SQL_SCHEMA_VERSION)
                        .scalar())
        except OperationalError:
            return False

    # ------------------------------------------------
    # Connects to database using connection string
    # ------------------------------------------------
    def connect(self, connection_string="mysql+mysqlconnector://rcdb@127.0.0.1/rcdb", check_version=True):
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

        try:
            self.engine = sqlalchemy.create_engine(connection_string)
        except ImportError, err:
            # sql alchemy uses MySQLdb by default. But it might be not install in the system
            # in such case we fallback to mysqlconnector which is embedded in CCDB
            if connection_string.startswith("mysql://") and "No module named MySQLdb" in repr(err):
                connection_string = connection_string.replace("mysql://", "mysql+mysqlconnector://")
                self.engine = sqlalchemy.create_engine(connection_string)
            else:
                raise

        session_type = sessionmaker(bind=self.engine)
        self.session = session_type()
        self._is_connected = True
        self._connection_string = connection_string

        if check_version:

            if not self.is_acceptable_sql_version():
                message = "SQL schema version doesn't match. " \
                          "Probably RCDB is connecting with wrong, empty or older/newer DB"
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
        :type table_ids:list[str] or list[ModelBase] or Base or str

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
    # Get run periods
    # ------------------------------------------------
    def get_run_periods(self):
        """Returns dict with run-periods

        :return: dict with {"name":(run_min, run_max, description)}
        """
        return rcdb.model.run_periods

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
        :type description: basestring

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
                self._cnd_types_by_name = None;
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

        return result+ignore_list

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

    def select_runs(self, search_str="", run_min=0, run_max=sys.maxsize, sort_desc=False):
        """ Searches RCDB for runs with e

        :param sort_desc: if True result runs will by sorted descendant by run_number, ascendant if False
        :param run_min: minimum run to search
        :param run_max: maximum run to search
        :param search_str: Search pattern
        :type search_str: str
        :return: List of runs matching criteria
        :rtype: list(Run)
        """
        start_time_stamp = int(mktime(datetime.datetime.now().timetuple()) * 1000)
        preparation_sw = StopWatchTimer()
        preparation_sw.start()

        if run_min > run_max:
            run_min, run_max = run_max, run_min

        # PHASE 0 - Maybe there is no query?!
        if not search_str or not search_str.strip():
            # If no query, just use get_runs function and return the result
            preparation_sw.stop()
            query_sw = StopWatchTimer()
            query_sw.start()
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
        query_sw.start()

        values = query.all()

        query_sw.stop()

        selection_sw = StopWatchTimer()
        selection_sw.start()

        # PHASE 3: Selecting runs
        compiled_search_eval = compile(search_eval, '<string>', 'eval')

        sel_runs = []

        for value in values:
            if isinstance(value, Condition):
                value = (value,)
            run = value[0].run
            if eval(compiled_search_eval):
                sel_runs.append(run)

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


class RunSelectionResult(MutableSequence):
    """Define a list format, which I can customize"""

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
        sw.start()

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
        sw.start()

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
    """
    RCDB data provider that uses SQLAlchemy for accessing databases
    """

    # ------------------------------------------------
    #
    # ------------------------------------------------
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

    # ---------------------------
    #
    # ---------------------------
    def obtain_crate(self, name):
        """
        Gets or creates crate with the name
        :param name: Crate name
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

    # -----------------------------------------------------
    #
    # ------------------------------------------------------
    def obtain_board_installation(self, crate, board, slot):
        """
        Gets board installation by crate, board, slot. Create a new one in DB
        if there is no such installation
        """
        # some validation and value checks
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
            self.add_log_record(installation,
                                "Board installation for crate='{}', board='{}', sn='{}', slot='{}' added to DB".format(
                                    crate.name, board.board_type, board.serial, slot),
                                0)
            return installation
        else:
            return query.first()

    # ------------------------------------------------
    #
    # ------------------------------------------------
    def obtain_dac_preset(self, board, values):
        """Gets or creates dac preset for board and dac values"""
        query = self.session.query(DacPreset) \
            .filter(DacPreset.board_id == board.id,
                    DacPreset.text_values == list_to_db_text(values))
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

    # ------------------------------------------------
    #
    # ------------------------------------------------
    def add_board_config_to_run(self, run, board, dac_preset):
        """sets that the board have the dac preset values in the run"""
        if not isinstance(run, Run):  # run is given as run number not Run object
            run = self.create_run(int(run))

        if not isinstance(dac_preset, DacPreset):
            dac_preset = self.obtain_dac_preset(board, dac_preset)

        # query = self.session.query(BoardConfiguration).join(BoardConfiguration.runs) \
        # .filter(RunConfiguration.id == run.id,
        # BoardConfiguration.board_id == board.id,
        # BoardConfiguration.dac_preset_id == dac_preset.id)

        query = self.session.query(BoardConfiguration) \
            .filter(BoardConfiguration.board_id == board.id,
                    BoardConfiguration.dac_preset_id == dac_preset.id)

        # Get or create board configuration
        if not query.count():
            log.debug(Lf("Board configuration for board.id='{}', dac_preset.id='{}' not found",
                         board.id, dac_preset.id))
            board_config = BoardConfiguration()
            board_config.board = board
            board_config.dac_preset = dac_preset
            self.session.add(board_config)
            self.session.commit()
            self.add_log_record([board_config, board, dac_preset],
                                "Board conf create. board.id='{}', dac_preset.id='{}'".format(board.id, dac_preset.id),
                                run.number)
        else:
            board_config = query.first()

        # check for run!
        if run not in board_config.runs:
            log.debug(Lf("Board configuration id='{}' not found in run='{}'", board_config.id, run.number))
            board_config.runs.append(run)
            self.session.commit()
            self.add_log_record(board_config,
                                "Board conf id='{}' added to run='{}'".format(board_config.id, run.number),
                                run.number)
        else:
            log.debug(Lf("Board configuration id='{}' is already in run='{}'", board_config.id, run.number))

    # ------------------------------------------------
    #
    # ------------------------------------------------
    def add_board_installation_to_run(self, run, board_installation):
        """Adds board installation to run using crate, board, slot
        :run: run number or RunConfiguration object
        :board_installation: board installation object
        """
        if isinstance(board_installation, tuple):
            # it is (crate, board, slot)
            crate, board, slot = board_installation
            board_installation = self.obtain_board_installation(crate, board, slot)

        if not isinstance(run, Run):  # run is given as run number not Run object
            run = self.create_run(int(run))
        assert isinstance(board_installation, BoardInstallation)

        if board_installation not in run.board_installations:
            log.debug(Lf("Board installation id='{}' is not associated with run='{}'",
                         board_installation.id, run.number))
            run.board_installations.append(board_installation)
            self.session.commit()
            self.add_log_record(board_installation,
                                "Add board_installation='{}' to run='{}'".format(board_installation.id, run.number),
                                run.number)
        else:
            log.debug(Lf("Board installation id='{}' already associated with run='{}'",
                         board_installation.id, run.number))

    # ------------------------------------------------
    #
    # ------------------------------------------------
    def add_run_statistics(self, run, total_events):
        """adds run statistics like total events number, etc"""
        if not isinstance(run, Run):  # run is given as run number not Run object
            run = self.create_run(int(run))

        run.total_events = total_events
        log.debug(Lf("Updating run statistics. total_events='{}'", total_events))

        self.session.commit()
        self.add_log_record(run, "Run statistics updated. total_events='{}'. Etc...".format(total_events), run.number)

    # ------------------------------------------------
    #
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
    #
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
    def add_configuration_file(self, run, path, content=None, overwrite=False):
        """Adds configuration file to run configuration. If such file exists
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
            log.debug(Lf("|- Content is None, assuming using file '{}'", path))
            check_sum = file_archiver.get_file_sha256(path)
        else:
            log.debug(Lf("|- Content is NOT none, using it to put to DB", path))
            check_sum = file_archiver.get_string_sha256(content)

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


def destroy_all_create_schema(db):
    """
    Creates RCDB schema in database. Used for test purpuses
    :param db: RCDBProvider provider
    :return:
    """
    assert isinstance(db, RCDBProvider)
    rcdb.model.Base.metadata.create_all(db.engine)
    v = SchemaVersion()
    v.version = rcdb.SQL_SCHEMA_VERSION
    v.comment = "Automatically created by 'def destroy_all_create_schema(db)'"
    db.session.add(v)
    db.session.commit()
