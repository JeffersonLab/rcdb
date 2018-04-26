from rcdb.model import ConditionType
import sqlalchemy
from sqlalchemy.orm import sessionmaker
# from .model import Board

from .provider import RCDBProvider
from .provider import ConfigurationProvider
from .errors import OverrideConditionTypeError, NoConditionTypeFound
from .errors import OverrideConditionValueError, NoRunFoundError, SqlSchemaVersionError
from sqlalchemy.orm.exc import NoResultFound
from rcdb.constants import START_COMMENT_RECORD_KEY, END_COMMENT_RECORD_KEY, COMPONENT_STAT_KEY, FADC250_KEY

# This thing separates cells in data blob
blob_delimiter = "|"

# if cell of data table is a string and the string already contains blob_delimiter
# we have to encode blob_delimiter to blob_delimiter_replace on data write and decode it bach on data read
blob_delimiter_replacement = "&delimiter;"

SQL_SCHEMA_VERSION = 1

SQL_ALEMBIC_VERSION = ''


class UpdateReasons(object):
    """Class holds a default values of UpdateContext.reason field
    Attributes:
        START -  means update goes after 'GO', beginning of the data taking
        UPDATE - after run in started, RCDB is being update each minute. That is how it is done
        END -    after run is ended
        """
    START = 'start'
    UPDATE = 'update'
    END = 'end'
    UNKNOWN = ''


# -------------------------------------------------
# class holding a context of the update operations
# -------------------------------------------------
class UpdateContext(object):
    """Updates context

        Attributes:
            self.db - RCDBProvider with connection
            self.reason - one of UpdateReasons or empty string
            self.run - Run object
    """

    def __init__(self, db, reason):
        self.db = db
        self.reason = reason  # Context in which daq is called '', 'start', 'update', 'end'
        self.run = None       # Run object


# -------------------------------------------------
# function Convert list to DB text representation
# -------------------------------------------------
def list_to_db_text(values):
    """
    Converts list of values like pedestal,threshold,baseline_preset values
    to a space separated string - that is how the values are stored in the DB

    :param values: list of values
    :type values: []

    :return: string with values as it is stored in DB
    :rtype: basestring
    """
    return " ".join([str(value) for value in values])


def make_threshold_preset(db, board, values):
    """
    checks if values
    :param values:
    :return:
    """

    if isinstance(values, list):
        text_values = list_to_db_text(values)


class DefaultConditions(object):
    """
    Holds common names for conditions and can ensure database have them
    """

    EVENT_RATE = 'event_rate'
    EVENT_COUNT = 'event_count'
    RUN_TYPE = 'run_type'
    RUN_CONFIG = 'run_config'
    RUN_LENGTH = 'run_length'
    RUN_START_TIME = 'run_start_time'
    RUN_END_TIME = 'run_end_time'
    DAQ_SETUP = 'daq_setup'
    SESSION = 'session'
    USER_COMMENT = 'user_comment'
    COMPONENTS = 'components'
    COMPONENT_STATS = 'component_stats'
    RTVS = 'rtvs'
    IS_VALID_RUN_END = 'is_valid_run_end'


def create_condition_types(db):
    """
    Checks if condition types listed in class exist in the database and create them if not
    :param db: RCDBProvider connected to database
    :type db: RCDBProvider

    :return: None
    """
    all_types_dict = {t.name: t for t in db.get_condition_types()}

    def create_condition_type(name, value_type, description=""):
        all_types_dict[name] if name in all_types_dict.keys() \
            else db.create_condition_type(name, value_type, description)

    # get or create condition type
    create_condition_type(DefaultConditions.EVENT_RATE, ConditionType.FLOAT_FIELD)
    create_condition_type(DefaultConditions.EVENT_COUNT, ConditionType.INT_FIELD)
    create_condition_type(DefaultConditions.RUN_TYPE, ConditionType.STRING_FIELD)
    create_condition_type(DefaultConditions.RUN_CONFIG, ConditionType.STRING_FIELD)
    create_condition_type(DefaultConditions.SESSION, ConditionType.STRING_FIELD)
    create_condition_type(DefaultConditions.USER_COMMENT, ConditionType.STRING_FIELD)
    create_condition_type(DefaultConditions.COMPONENTS, ConditionType.JSON_FIELD)
    create_condition_type(DefaultConditions.RTVS, ConditionType.JSON_FIELD)
    create_condition_type(DefaultConditions.COMPONENT_STATS, ConditionType.JSON_FIELD)
    create_condition_type(DefaultConditions.IS_VALID_RUN_END, ConditionType.BOOL_FIELD,
                          "True if a run has valid run-end record. "
                          "False means the run was aborted/crashed at some point")
    create_condition_type(DefaultConditions.RUN_LENGTH, ConditionType.INT_FIELD, "Length of the run ")
    create_condition_type(DefaultConditions.RUN_START_TIME, ConditionType.TIME_FIELD, "Run start time ")
    create_condition_type(DefaultConditions.RUN_END_TIME, ConditionType.TIME_FIELD, "Run end time (last CODA update)")

