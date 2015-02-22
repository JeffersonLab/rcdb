import datetime
import posixpath

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Text, DateTime, Enum, Float, Boolean, UnicodeText
from sqlalchemy.orm import sessionmaker, reconstructor
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import desc
from sqlalchemy.ext.declarative import declared_attr

Base = declarative_base()

class ModelBase(Base):
    __abstract__ = True

    @property
    def log_id(self):
        """returns id suitable for log. Which is tablename_id"""
        return self.__tablename__ + "_" + str(self.id)



# objects for many to many association
_board_conf_have_runs_association = Table('board_configurations_have_runs', Base.metadata,
                                          Column('board_configuration_id', Integer,
                                                 ForeignKey('board_configurations.id')),
                                          Column('run_number', Integer, ForeignKey('runs.number')))

_board_inst_have_runs_association = Table('board_installations_have_runs', Base.metadata,
                                          Column('board_installation_id', Integer,
                                                 ForeignKey('board_installations.id')),
                                          Column('run_number', Integer, ForeignKey('runs.number')))

_files_have_runs_association = Table('files_have_runs', Base.metadata,
                                     Column('files_id', Integer, ForeignKey('files.id')),
                                     Column('run_number', Integer, ForeignKey('runs.number')))


def _count_version(context, table_name):
    """ counts a number of previous configuration """
    assert isinstance(table_name, basestring)
    board_id = context.current_parameters["board_id"]
    result = context.engine.execute("SELECT count(*) AS n FROM " + table_name + " WHERE board_id=%s", str(board_id))
    for row in result:
        context.current_parameters["version"] = int(row['n'])
        return int(row['n'])


#--------------------------------------------
# class Board
#--------------------------------------------
class Board(ModelBase):
    """
    Represents trigger DB board.
    """
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True)
    serial = Column(String(512))
    board_type = Column(String(45))
    modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    readout_thresholds = relationship("ReadoutThresholdPreset", cascade="all, delete, delete-orphan")
    trigger_thresholds = relationship("TriggerThresholdPreset", cascade="all, delete, delete-orphan")
    readout_masks = relationship("ReadoutMaskPreset", cascade="all, delete, delete-orphan")
    trigger_masks = relationship("TriggerMaskPreset", cascade="all, delete, delete-orphan")
    dac_presets = relationship("DacPreset", cascade="all, delete, delete-orphan")
    configs = relationship("BoardConfiguration", cascade="all, delete, delete-orphan", back_populates="board")
    installations = relationship("BoardInstallation", cascade="all, delete, delete-orphan", back_populates="board")

    def __repr__(self):
        return "<Board id='{0}' name='{1}'>".format(self.id, self.board_name)


#--------------------------------------------
# class Crate
#--------------------------------------------
class Crate(ModelBase):
    """
    Represents Crate where boards are placed
    """
    __tablename__ = 'crates'
    id = Column(Integer, primary_key=True)
    name = Column(String(45))
    created = Column(DateTime, default=datetime.datetime.now)
    installations = relationship("BoardInstallation", cascade="all, delete, delete-orphan", back_populates="crate")


#--------------------------------------------
# class BoardInstallation
#--------------------------------------------
class BoardInstallation(ModelBase):
    """
    Represents board installation
    """
    __tablename__ = 'board_installations'
    id = Column(Integer, primary_key=True)
    board_id = Column(Integer, ForeignKey('boards.id'))
    board = relationship("Board", back_populates="installations")
    crate_id = Column(Integer, ForeignKey('crates.id'))
    crate = relationship("Crate", back_populates="installations")
    slot = Column(Integer)
    runs = relationship("Run",
                        secondary=_board_inst_have_runs_association,
                        back_populates="board_installations")

#--------------------------------------------
# class PerChannelData
#--------------------------------------------
class PerChannelPresetMixin(object):
    id = Column(Integer, primary_key=True)
    text_values = Column('values', String(1024))

    @declared_attr
    def board_id(cls):
        return Column(Integer, ForeignKey('boards.id'), nullable=False)

    version = Column(Integer, default=0)  # lambda context: _count_version(context, 'dac_presets'))

    @property
    def values(self):
        """:return: list with pedestal values as strings"""
        return str(self.text_values).split()

    @values.setter
    def values(self, values):
        self.text_values = list_to_db_text(list(values))

    def _get_next_version(self):
        return len(self.board.threshold_presets)

    def __repr__(self):
        return "<PerChannelPreset id='{0}' table='{1}'>".format(self.id, self.__tablename__)


#--------------------------------------------
# Per channel preset classes
#--------------------------------------------
class DacPreset(PerChannelPresetMixin, Base):
    __tablename__ = 'dac_presets'


class ReadoutThresholdPreset(PerChannelPresetMixin, Base):
    __tablename__ = 'readout_thresholds'


class TriggerThresholdPreset(PerChannelPresetMixin, Base):
    __tablename__ = 'trigger_thresholds'


class ReadoutMaskPreset(PerChannelPresetMixin, Base):
    __tablename__ = 'readout_masks'


class TriggerMaskPreset(PerChannelPresetMixin, Base):
    __tablename__ = 'trigger_masks'



#--------------------------------------------
# class
#--------------------------------------------
class BoardConfiguration(ModelBase):
    """

    """
    __tablename__ = 'board_configurations'
    id = Column(Integer, primary_key=True)
    readout_thresholds_id = Column("readout_threshold_id", Integer, ForeignKey('readout_thresholds.id'), nullable=True)
    readout_threshold_preset = relationship("ReadoutThresholdPreset")

    trigger_thresholds_id = Column("trigger_threshold_id", Integer, ForeignKey('trigger_thresholds.id'), nullable=True)
    trigger_threshold_preset = relationship("TriggerThresholdPreset")

    readout_masks_id = Column("readout_mask_id", Integer, ForeignKey('readout_masks.id'), nullable=True)
    readout_mask_preset = relationship("ReadoutMaskPreset")

    trigger_masks_id = Column("trigger_mask_id", Integer, ForeignKey('trigger_masks.id'), nullable=True)
    trigger_mask_preset = relationship("TriggerMaskPreset")

    dac_preset_id = Column(Integer, ForeignKey('dac_presets.id'), nullable=True)
    dac_preset = relationship("DacPreset")

    #_parameters_id = Column("board_parameters_id", Integer, ForeignKey('board_parameters.id'), nullable=True)
    #parameter_preset = relationship("BoardParameterPreset")

    board_id = Column(Integer, ForeignKey('boards.id'))
    board = relationship("Board", back_populates="configs")
    runs = relationship("Run",
                        secondary=_board_conf_have_runs_association,
                        back_populates="board_configs")
    version = Column(Integer, default=0)  # lambda context:_count_version(context, 'board_configurations'))

    @property
    def log_id(self):
        """returns id suitable for log. Which is tablename_id"""
        return self.__tablename__ + "_" + str(self.id)

    def __repr__(self):
        return "<BoardConfiguration id='{0}'>".format(self.id)


#--------------------------------------------
# class RUN
#--------------------------------------------
class Run(ModelBase):
    """

    """
    __tablename__ = 'runs'

    number = Column(Integer, primary_key=True, unique=True, autoincrement=False)
    """The run number"""

    #
    board_configs = relationship("BoardConfiguration", secondary=_board_conf_have_runs_association,
                                 back_populates="runs")
    """Link to board channels and etc. configured for the run"""

    #
    board_installations = relationship("BoardInstallation",
                                       secondary=_board_inst_have_runs_association,
                                       order_by=lambda: BoardInstallation.crate_id,
                                       back_populates="runs")
    """Link to crate and slot information for the board"""

    #
    files = relationship("ConfigurationFile", secondary=_files_have_runs_association, back_populates="runs")
    """Configuration and log files associated with the run"""

    #_trigger_config_id = Column('trigger_configuration_id', Integer, ForeignKey('trigger_configurations.id'), nullable=True)
    #trigger = relationship("TriggerConfiguration",  back_populates="runs")

    #
    start_time = Column('started', DateTime, nullable=True)
    """Run start time"""

    #
    end_time = Column('finished', DateTime, nullable=True)
    """Run end time"""

    #
    conditions = relationship("Condition", back_populates="run")
    """Conditions associated with the run"""

    #total_events = Column(Integer, nullable=False, default=0)

    #@property
    #def records_map(self):
    #    """
    #    :return: map with pedestal values as strings
    #    :rtype:  {str:Condition}
    #    """
    #   rbt = {record.key: record for record in self.records}
    #   return rbt

    @property
    def log_id(self):
        """returns id suitable for log. Which is tablename_id"""
        return self.__tablename__ + "_" + str(self.number)

    def __repr__(self):
        return "<Run id='{0}'>".format(self.id)


#--------------------------------------------
# class
#--------------------------------------------
class ConfigurationFile(ModelBase):
    """
    Table contains original coda and board configuration files
    """
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    sha256 = Column(String(44), nullable=False)
    content = Column(String(convert_unicode=True), nullable=False)
    description = Column(String(255), nullable=True)
    runs = relationship("Run", secondary=_files_have_runs_association, back_populates="files")

    def __repr__(self):
        return "<ConfigurationFile id='{0}', path='{1}'>".format(self.id, self.path)


#
# #--------------------------------------------
# # class
# #--------------------------------------------
# class TriggerConfiguration(Base):
#     """
#     Holds information about trigger configuration for this run
#     """
#     __tablename__ = 'trigger_configurations'
#     id = Column(Integer, primary_key=True)
#     type = Column(String, nullable=False)
#     runs = relationship("Run",  back_populates="trigger")
#
#     def __repr__(self):
#         return "<TriggerConfiguration id='{0}'>".format(self.id)
#

class ConditionType(ModelBase):
    """
    Holds type and constants name of data attached to particular run.
    :see Condition
    : BOOL_FIELD: Ha ha ha, test it
    :type BOOL_FIEL

    """

    #: Boolean field. Is used for declaration of value_type
    BOOL_FIELD = "bool"

    JSON_FIELD = "json"
    """JSON field. It is a string constant using for declaration of value_type"""

    STRING_FIELD = "string"
    """String field. It is a string constant using for declaration of value_type"""

    FLOAT_FIELD = "float"
    """Float field. It is a string constant using for declaration of value_type"""

    INT_FIELD = "int"
    """Integer field. It is a string constant using for declaration of value_type"""

    __tablename__ = 'condition_types'
    """Name of the database table"""

    id = Column(Integer, primary_key=True)
    """DB id"""

    name = Column(String(255), nullable=False)
    """Key. Or constant name"""

    value_type = Column(Enum(JSON_FIELD, STRING_FIELD, FLOAT_FIELD, INT_FIELD, BOOL_FIELD, native_enum=False),
                        nullable=False, default=STRING_FIELD)
    """Type of constant. Might be one of JSON_FIELD, STRING_FIELD, FLOAT_FIELD, INT_FIELD, BOOL_FIELD"""

    is_many_per_run = Column(Boolean, nullable=False, default=True)
    """True if the value is allowed only one per run"""

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


class Condition(ModelBase):
    """
    Holds information attached to particular run.
    Such as start comments, end comments, statistics, etc...
    :see ConditionType
    """

    __tablename__ = 'conditions'
    id = Column(Integer, primary_key=True)

    text_value = Column(String, nullable=True, default=None)
    int_value = Column(Integer, nullable=False, default=0)
    float_value = Column(Float, nullable=False, default=0.0)
    bool_value = Column(Boolean, nullable=False, default=False)
    time = Column(DateTime, nullable=True, default=None)

    run_number = Column(Integer, ForeignKey('runs.number'))
    run = relationship("Run", back_populates="conditions")

    _condition_type_id = Column('condition_type_id', Integer, ForeignKey('condition_types.id'))
    type = relationship("ConditionType", back_populates="values")
    """:type: ConditionType"""

    created = Column(DateTime, default=datetime.datetime.now)

    @hybrid_property
    def name(self):
        return self.type.name

    @hybrid_property
    def value_type(self):
        return self.type.value_type

    @hybrid_property
    def value(self):
        """ Gets value of the corrected type """
        field_type = self.type.value_type
        if field_type == ConditionType.INT_FIELD:
            return self.int_value
        if field_type == ConditionType.STRING_FIELD or field_type == ConditionType.JSON_FIELD:
            return self.text_value
        if field_type == ConditionType.FLOAT_FIELD:
            return self.float_value
        if field_type == ConditionType.BOOL_FIELD:
            return self.bool_value
        return self.text_value

    @value.setter
    def value(self, val):
        """ Gets value of the corrected type """
        field_type = self.type.value_type
        if field_type == ConditionType.INT_FIELD:
            self.int_value = val
        elif field_type == ConditionType.STRING_FIELD or field_type == ConditionType.JSON_FIELD:
            self.text_value = val
        elif field_type == ConditionType.FLOAT_FIELD:
            self.float_value = val
        elif field_type == ConditionType.BOOL_FIELD:
            self.bool_value = val
        else:
            raise ValueError("Unknown field type! field_type='{}'".format(field_type))


    def __repr__(self):
        return "<Condition id='{id}', run_number='{run_number}', value={value}>".format(self)


class LogRecord(ModelBase):
    """
    RunInfo:
    Holds information attached to particular run. Such as start comments,
    end comments, statistics, etc...
    """
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    table_ids = Column(String(255))
    description = Column(String)
    related_run_number = Column('related_run', Integer, nullable=True)
    created = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return "<LogRecord id='{0}', description='{1}'>".format(self.id, self.description)


#-------------------------------------------------
# function Convert list to DB text representation
#-------------------------------------------------
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


