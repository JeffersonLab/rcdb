import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Text, DateTime, Enum, Float, Boolean, UnicodeText
from sqlalchemy.orm import sessionmaker, reconstructor, object_session
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import desc
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.expression import func

Base = declarative_base()


class ModelBase(Base):
    __abstract__ = True

    @property
    def log_id(self):
        """returns id suitable for log. Which is tablename_id"""
        return self.__tablename__ + "_" + str(self.id)


_files_have_runs_association = Table('files_have_runs', Base.metadata,
                                     Column('files_id', Integer, ForeignKey('files.id')),
                                     Column('run_number', Integer, ForeignKey('runs.number')))

# --------------------------------------------
# class RUN
# --------------------------------------------
class Run(ModelBase):
    """
    Represents data for run

    Attributes:
        Run.number (int): The run number

    """
    __tablename__ = 'runs'

    number = Column(Integer, primary_key=True, unique=True, autoincrement=False)

    #
    files = relationship("ConfigurationFile", secondary=_files_have_runs_association, back_populates="runs")
    """[ConfigurationFile]: Configuration and log files associated with the run"""

    #
    start_time = Column('started', DateTime, nullable=True)
    """Run start time"""

    #
    end_time = Column('finished', DateTime, nullable=True)
    """Run end time"""

    #
    conditions = relationship("Condition", back_populates="run")
    """Conditions associated with the run"""

    def __init__(self):
        self._conditions_by_name = None

    @reconstructor
    def init_on_load(self):
        self._conditions_by_name = None

    @property
    def log_id(self):
        """returns id suitable for log. Which is tablename_id"""
        return self.__tablename__ + "_" + str(self.number)

    def get_conditions_by_name(self):
        """
        Create and returns dictionary of condition.name -> condition

        Returns:
            dict[str, Condition]: Dictionary where key is condition.name and value is condition
        """
        d = dict()
        for condition in self.conditions:
            d[condition.name] = condition
        return d

    def get_condition(self, condition_name):
        """ Gets the Condition object by name if such name condition exist for the run. Null otherwise

        :param condition_name: The condition name
        :type condition_name: string
        :return: Condition for this name for run or null
        :rtype: Condition or None
        """
        if self._conditions_by_name is None:
            self._conditions_by_name = self.get_conditions_by_name()

        return self._conditions_by_name[condition_name] \
            if condition_name in self._conditions_by_name.keys() \
            else None

    def get_condition_value(self, condition_name):
        """ Gets the condition value if such name condition exist for the run. Null otherwise

        :param condition_name: The condition name
        :type condition_name: string
        :return: Condition value for this name for run or None

        """
        cnd = self.get_condition(condition_name)
        return cnd.value if cnd is not None else None

    def __repr__(self):
        return "<Run number='{0}'>".format(self.number)


# --------------------------------------------
# class
# --------------------------------------------
class ConfigurationFile(ModelBase):
    """
    Table contains original coda and board configuration files
    """

    IMPORTANCE_HIGH = 0
    IMPORTANCE_LOW = 1
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    path = Column(Text, nullable=False)
    sha256 = Column(String(44), nullable=False)
    content = Column(Text(), nullable=False)
    description = Column(String(255), nullable=True)
    importance = Column(Integer, nullable=False, default=0, server_default='0')
    runs = relationship("Run", secondary=_files_have_runs_association, back_populates="files")

    def __repr__(self):
        return "<ConfigurationFile id='{0}', path='{1}'>".format(self.id, self.path)


class ConditionType(ModelBase):
    """
    Holds type and constants name of data attached to particular run.
    """

    # Constants to represent the type of the field
    BOOL_FIELD = "bool"
    JSON_FIELD = "json"
    STRING_FIELD = "string"
    FLOAT_FIELD = "float"
    INT_FIELD = "int"
    TIME_FIELD = "time"
    BLOB_FIELD = "blob"

    __tablename__ = 'condition_types'
    """Name of the database table"""

    id = Column(Integer, primary_key=True)
    """DB id"""

    name = Column(String(255), nullable=False)
    """Key. Or constant name"""

    value_type = Column(Enum(JSON_FIELD, STRING_FIELD, FLOAT_FIELD, INT_FIELD, BOOL_FIELD, TIME_FIELD, BLOB_FIELD,
                             native_enum=False),
                        nullable=False, default=STRING_FIELD)
    """Type of constant. Might be one of:
     JSON_FIELD, STRING_FIELD, FLOAT_FIELD, INT_FIELD, BOOL_FIELD, TIME_FIELD, BLOB_FIELD"""

    created = Column(DateTime, default=datetime.datetime.now)
    """Time of creation (set automatically)"""

    values = relationship("Condition", back_populates="type", lazy="dynamic", cascade="all")
    """Values of this type attached to runs.

        Since there are many runs, the load strategy is lazy="dynamic" this means that
        values are queryable.

        Example:
        -------
            db = rcdb.ConfigurationProvider("mysql://rcdb@127.0.0.1/rcdb")
            condition_type = db.get_condition_type("total_event_count")

            #get condition values for
            condition_type.values.filter(Condition.run.number > 5000)
    """

    description = Column(String(255), nullable=True)

    @property
    def run_query(self):
        return object_session(self).query(Run) \
            .join(Condition, Condition.run_number == Run.number) \
            .filter(Condition.type == self)

    def get_condition_alias_value_field(self, alias):
        """ Gets appropriate aliased(Condition).xxx_value field according to type """
        field = None
        if self.value_type == ConditionType.INT_FIELD:
            field = alias.int_value
        if self.value_type == ConditionType.STRING_FIELD \
                or self.value_type == ConditionType.JSON_FIELD \
                or self.value_type == ConditionType.BLOB_FIELD:
            field = alias.text_value
        if self.value_type == ConditionType.FLOAT_FIELD:
            field = alias.float_value
        if self.value_type == ConditionType.BOOL_FIELD:
            field = alias.bool_value
        if self.value_type == ConditionType.TIME_FIELD:
            field = alias.time_value
        return field

    def get_value_field_name(self):
        """ Gets appropriate aliased(Condition).xxx_value field according to type """
        name = None
        if self.value_type == ConditionType.INT_FIELD:
            name = 'int_value'
        if self.value_type == ConditionType.STRING_FIELD \
                or self.value_type == ConditionType.JSON_FIELD \
                or self.value_type == ConditionType.BLOB_FIELD:
            name = 'text_value'
        if self.value_type == ConditionType.FLOAT_FIELD:
            name = 'float_value'
        if self.value_type == ConditionType.BOOL_FIELD:
            name = 'bool_value'
        if self.value_type == ConditionType.TIME_FIELD:
            name = 'time_value'
        return name

    @hybrid_property
    def value_field(self):
        """ Gets appropriate Condition.xxx_value field according to type """
        field = None
        if self.value_type == ConditionType.INT_FIELD:
            field = Condition.int_value
        if self.value_type == ConditionType.STRING_FIELD \
                or self.value_type == ConditionType.JSON_FIELD \
                or self.value_type == ConditionType.BLOB_FIELD:
            field = Condition.text_value
        if self.value_type == ConditionType.FLOAT_FIELD:
            field = Condition.float_value
        if self.value_type == ConditionType.BOOL_FIELD:
            field = Condition.bool_value
        if self.value_type == ConditionType.TIME_FIELD:
            field = Condition.time_value
        return field

    def convert_value(self, value):
        # validate value
        if self.value_type == ConditionType.FLOAT_FIELD:
            try:
                value = float(value)
            except ValueError as err:
                message = "Condition type '{}' awaits float as value. {}".format(self, err)
                raise ValueError(message)
        elif self.value_type == ConditionType.INT_FIELD:
            try:
                value = int(value)
            except ValueError as err:
                message = "Condition type '{}' awaits int as value. {}".format(self, err)
                raise ValueError(message)
        elif self.value_type == ConditionType.TIME_FIELD and not isinstance(value, datetime.datetime):
            message = "Condition type '{}' awaits datetime as value. '{}' is given".format(self, type(value))
            raise ValueError(message)
        elif self.value_type == ConditionType.BOOL_FIELD:
            try:
                value = bool(value)
            except ValueError as err:
                message = "Condition type '{}' awaits bool as value. {}".format(self, err)
                raise ValueError(message)
        return value

    def values_are_equal(self, left_value, right_value):
        """Function compares 2 values and return true if values are differ.
        The function takes in account floating point comparison if value_type is FLOAT_FIELD
        Also it validates both values

        :param left_value: Left value. Could be Condition object
        :param right_value: Right value. Could be Condition object"""

        if isinstance(left_value, Condition):
            left_value = left_value.value
        if isinstance(right_value, Condition):
            right_value = right_value.value

        left_value = self.convert_value(left_value)
        right_value = self.convert_value(right_value)

        # if value is float, use precision
        if self.value_type == ConditionType.FLOAT_FIELD:
            return is_close(left_value, right_value)
        else:
            return left_value == right_value

    def __repr__(self):
        return "<ConditionType id='{}', name='{}', value_type={}>" \
            .format(self.id, self.name, self.value_type)


all_value_types = [
    ConditionType.BOOL_FIELD,
    ConditionType.JSON_FIELD,
    ConditionType.STRING_FIELD,
    ConditionType.FLOAT_FIELD,
    ConditionType.INT_FIELD,
    ConditionType.TIME_FIELD,
    ConditionType.BLOB_FIELD,
]


class Condition(ModelBase):
    """
    Holds information attached to particular run.
    Such as start comments, end comments, statistics, etc...
    :see ConditionType
    """

    __tablename__ = 'conditions'
    id = Column(Integer, primary_key=True)

    text_value = Column(Text, nullable=True, default=None)
    int_value = Column(Integer, nullable=False, default=0)
    float_value = Column(Float, nullable=False, default=0.0)
    bool_value = Column(Boolean, nullable=False, default=False)
    time_value = Column(DateTime, nullable=True, default=None)

    run_number = Column(Integer, ForeignKey('runs.number'))
    run = relationship("Run", back_populates="conditions")

    condition_type_id = Column('condition_type_id', Integer, ForeignKey('condition_types.id'))
    type = relationship("ConditionType", back_populates="values")
    """:type: ConditionType"""

    created = Column(DateTime, default=datetime.datetime.now)

    @hybrid_property
    def name(self):
        return self.type.name

    @name.expression
    def balance(self):
        return ConditionType.name

    @hybrid_property
    def value_type(self):
        return self.type.value_type

    @hybrid_property
    def value(self):
        """ Gets value of the corrected type """
        field_type = self.type.value_type
        if field_type == ConditionType.INT_FIELD:
            return self.int_value
        if field_type == ConditionType.STRING_FIELD \
                or field_type == ConditionType.JSON_FIELD \
                or field_type == ConditionType.BLOB_FIELD:
            return self.text_value
        if field_type == ConditionType.FLOAT_FIELD:
            return self.float_value
        if field_type == ConditionType.BOOL_FIELD:
            return self.bool_value
        if field_type == ConditionType.TIME_FIELD:
            return self.time_value
        return self.text_value

    @value.setter
    def value(self, val):
        """ Gets value of the corrected type """
        field_type = self.type.value_type
        if field_type == ConditionType.INT_FIELD:
            self.int_value = val
        elif field_type == ConditionType.STRING_FIELD \
                or field_type == ConditionType.JSON_FIELD \
                or field_type == ConditionType.BLOB_FIELD:
            self.text_value = val
        elif field_type == ConditionType.FLOAT_FIELD:
            self.float_value = val
        elif field_type == ConditionType.BOOL_FIELD:
            self.bool_value = val
        elif field_type == ConditionType.TIME_FIELD:
            self.time_value = val
        else:
            raise ValueError("Unknown field type! field_type='{}'".format(field_type))

    def __repr__(self):
        return "<Condition id='{}', run_number='{}', value={}>".format(self.id, self.run_number, self.value)


class SchemaVersion(ModelBase):
    __tablename__ = 'schema_versions'
    version = Column(Integer, primary_key=True, autoincrement=False)
    created = Column(DateTime)
    comment = Column(String(255), nullable=True)


class LogRecord(ModelBase):
    """
    RunInfo:
    Holds information attached to particular run. Such as start comments,
    end comments, statistics, etc...
    """
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    table_ids = Column(String(255))
    description = Column(Text)
    related_run_number = Column('related_run', Integer, nullable=True)
    created = Column(DateTime, default=datetime.datetime.now)
    user_name = Column(String(255), nullable=True)

    def __repr__(self):
        return "<LogRecord id='{0}', description='{1}'>".format(self.id, self.description)


run_periods = {
    "2017-01": (30000, 39999, "23 Jan 2017 - 13 Mar 2017   12 GeV e-"),
    "2016-10": (20000, 29999, "15 Sep 2016 - 21 Dec 2016   12 GeV e-"),
    "2016-02": (10000, 19999, "28 Jan 2016 - 24 Apr 2016   Commissioning, 12 GeV e-"),
    "2015-12": (3939, 4807,   "01 Dec 2015 - 28 Jan 2016   Commissioning, 12 GeV e-, Cosmics"),
    "2015-06": (3386, 3938,   "29 May 2015 - 01 Dec 2015   Cosmics"),
    "2015-03": (2607, 3385,   "11 Mar 2015 - 29 May 2015   Commissioning, 5.5 GeV e-"),
    "2015-01": (2440, 2606,   "06 Feb 2015 - 11 Mar 2015   Cosmics"),
    "2014-10": (630, 2439,    "28 Oct 2014 - 21 Dec 2014   Commissioning, 10 GeV e-"),
}


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


def dic_to_db_text(values):
    """
    Converts dictionary of str-double pairs like named parameters to ';' separated string
    that is how values are stored in the DB
    """
    assert isinstance(values, dict)
    return "; ".join([str(key) + "=" + str(value) for key, value in sorted(values.items())])


def db_text_to_dic(value_str):
    """
    gets text of format "a=5; b=4" and returns a dictionary {"a":"5", "b":"4"}

    :return: {}
    >>>db_text_to_dic("a=5; b=4")
    {"a":"5", "b":"4"}
    """
    assert isinstance(value_str, str)
    tokens = filter(None, value_str.replace(" ", ";").split(";"))  # gives like ['a=4', 'b=5.4']
    result = {}
    for token in tokens:
        key, value = token.split("=")
        result[key] = value
    return result


def db_text_to_float_dic(value_str):
    return {key: float(value) for key, value in db_text_to_dic(value_str).items()}


def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    """PEP 0485 -- A Function for testing approximate equality
    :param b: 1st value to compare
    :param a: 2nd value to compare
    :param rel_tol: is a relative tolerance, it is multiplied by the greater of the magnitudes of the two arguments;
    :param abs_tol: is an absolute tolerance that is applied as-is in all cases. If the difference is less than either
    of those tolerances, the values are considered equal

    rel_tol is a relative tolerance, it is multiplied by the greater of the magnitudes of the two arguments;
    as the values get larger, so does the allowed difference between them while still considering them equal.
    abs_tol is an absolute tolerance that is applied as-is in all cases. If the difference is less than either
    of those tolerances, the values are considered equal

    """
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
