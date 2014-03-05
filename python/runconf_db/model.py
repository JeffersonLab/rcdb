import datetime
import posixpath

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Text, DateTime, Enum, UnicodeText
from sqlalchemy.orm import sessionmaker, reconstructor
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import desc


Base = declarative_base()

#objects for many to many association
_board_conf_has_run_conf_association = Table('board_configurations_has_run_configurations', Base.metadata,
                                             Column('board_configuration_id', Integer, ForeignKey('board_configurations.id')),
                                             Column('run_configuration_id', Integer, ForeignKey('run_configurations.id')))


_board_inst_has_run_conf_association = Table('board_installations_has_run_configurations', Base.metadata,
                                             Column('board_installation_id', Integer, ForeignKey('board_installations.id')),
                                             Column('run_configuration_id', Integer, ForeignKey('run_configurations.id')))


_files_has_run_conf_association = Table('files_has_run_configurations', Base.metadata,
                                             Column('file_id', Integer, ForeignKey('files.id')),
                                             Column('run_configuration_id', Integer, ForeignKey('run_configurations.id')))



def _count_dacs(context):
    return _count_version(context, "dacs")


def _count_readout_thresholds(context):
    return _count_version(context, "readout_thresholds")


def _count_trigger_thresholds(context):
    return _count_version(context, "trigger_thresholds")


def _count_readout_masks(context):
    return _count_version(context, "readout_masks")


def _count_trigger_masks(context):
    return _count_version(context, "trigger_masks")


def _count_board_parameters(context):
    return  _count_version(context, "board_parameters")


def _count_version(context, table_name):
    assert isinstance(table_name, basestring)
    board_id = context.current_parameters["board_id"]
    result = context.engine.execute("SELECT count(*) AS n FROM "+table_name+" WHERE board_id=?", board_id)
    for row in result:
        context.current_parameters["version"] = int(row['n'])

#
# #--------------------------------------------
# # class Board
# #--------------------------------------------
# class Board(Base):
#     """
#     Represents trigger DB board.
#     """
#     __tablename__ = 'boards'
#     id = Column(Integer, primary_key=True)
#     board_name = Column('name', String(1024))
#     serial = Column(String(512))
#     board_type = Column(String(45))
#     description = Column(String(1024))
#     firmware = Column(String(45))
#     modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
#     readout_thresholds = relationship("ReadoutThresholdPreset", cascade="all, delete, delete-orphan")
#     trigger_thresholds = relationship("TriggerThresholdPreset", cascade="all, delete, delete-orphan")
#     readout_masks = relationship("ReadoutMaskPreset", cascade="all, delete, delete-orphan")
#     trigger_masks = relationship("TriggerMaskPreset", cascade="all, delete, delete-orphan")
#     dacs = relationship("DacPreset", cascade="all, delete, delete-orphan")
#     configs = relationship("BoardConfiguration", cascade="all, delete, delete-orphan")
#     installations = relationship("BoardInstallation", cascade="all, delete, delete-orphan")
#
#     def __repr__(self):
#         return "<Board id='{0}' name='{1}'>".format(self.id, self.board_name)
#
#
# #--------------------------------------------
# # class Crate
# #--------------------------------------------
# class Crate(Base):
#     """
#     Represents Crate where boards are placed
#     """
#     __tablename__ = 'crates'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(45))
#     installations = relationship("BoardInstallation", cascade="all, delete, delete-orphan")
#
#
# #--------------------------------------------
# # class BoardInstallation
# #--------------------------------------------
# class BoardInstallation(Base):
#     """
#     Represents board installation
#     """
#     __tablename__ = 'board_installations'
#     id = Column(Integer, primary_key=True)
#
#     board_id = Column(Integer, ForeignKey('boards.id'))
#     board = relationship("Board")
#     crate_id = Column(Integer, ForeignKey('crates.id'))
#     crate = relationship("Crate")
#     run_configs = relationship("RunConfiguration", secondary=_board_inst_has_run_conf_association)
#
#
# #--------------------------------------------
# # class DacPreset
# #--------------------------------------------
# class BoardParameterPreset(Base):
#     """
#     Parameter values for the board
#     """
#     __tablename__ = 'board_parameters'
#     id = Column(Integer, primary_key=True)
#     text_values = Column('values', String())
#
#     board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
#     board = relationship("Board")
#
#     version = Column(Integer, default=_count_board_parameters)
#
#     @property
#     def values(self):
#         """
#         :return: dictionary with pedestal values as strings
#         :rtype:  dict
#         """
#         return str(self.text_values).split()
#
#     @values.setter
#     def values(self, values):
#         assert (isinstance(values, list))
#         self.text_values = list_to_db_text(values)
#
#     def _get_next_version(self):
#         return len(self.board.threshold_presets)
#
#     def __repr__(self):
#         return "<DacPreset id='{0}'>".format(self.id)
#
#
#
# #--------------------------------------------
# # class DacPreset
# #--------------------------------------------
# class DacPreset(Base):
#     """
#     DacPreset a preset of threshold values
#     """
#     __tablename__ = 'dacs'
#     id = Column(Integer, primary_key=True)
#     text_values = Column('values', String(1024))
#
#     board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
#     board = relationship("Board")
#
#     version = Column(Integer, default=_count_dacs)
#
#     @property
#     def values(self):
#         """
#         :return: list with pedestal values as strings
#         :rtype:  list
#         """
#         return str(self.text_values).split()
#
#     @values.setter
#     def values(self, values):
#         assert (isinstance(values, list))
#         self.text_values = list_to_db_text(values)
#
#     def _get_next_version(self):
#         return len(self.board.threshold_presets)
#
#     def __repr__(self):
#         return "<DacPreset id='{0}'>".format(self.id)
#
#
# #--------------------------------------------
# # class ReadoutThresholdPreset
# #--------------------------------------------
# class ReadoutThresholdPreset(Base):
#     """
#     ReadoutThresholdPreset a preset of threshold values
#     """
#     __tablename__ = 'readout_thresholds'
#     id = Column(Integer, primary_key=True)
#     text_values = Column('values', String(1024))
#
#     board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
#     board = relationship("Board", backref("readout_thresholds"))
#
#     version = Column(Integer, default=_count_readout_thresholds)
#
#     @property
#     def values(self):
#         """
#         :return: list with pedestal values as strings
#         :rtype:  list
#         """
#         return str(self.text_values).split()
#
#     @values.setter
#     def values(self, values):
#         assert (isinstance(values, list))
#         self.text_values = list_to_db_text(values)
#
#     def _get_next_version(self):
#         return len(self.board.threshold_presets)
#
#     def __repr__(self):
#         return "<ReadoutThresholdPreset id='{0}'>".format(self.id)
#
#
# #--------------------------------------------
# # class ReadoutThresholdPreset
# #--------------------------------------------
# class TriggerThresholdPreset(Base):
#     """
#     ReadoutThresholdPreset a preset of threshold values
#     """
#     __tablename__ = 'trigger_thresholds'
#     id = Column(Integer, primary_key=True)
#     text_values = Column('values', String(1024))
#
#     board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
#     board = relationship("Board")
#
#     version = Column(Integer, default=_count_trigger_thresholds)
#
#     @property
#     def values(self):
#         """
#         :return: list with pedestal values as strings
#         :rtype:  list
#         """
#         return str(self.text_values).split()
#
#     @values.setter
#     def values(self, values):
#         assert (isinstance(values, list))
#         self.text_values = list_to_db_text(values)
#
#     def _get_next_version(self):
#         return len(self.board.threshold_presets)
#
#     def __repr__(self):
#         return "<TriggerThresholdPreset id='{0}'>".format(self.id)
#
#
# #--------------------------------------------
# # class ReadoutMaskPreset
# #--------------------------------------------
# class ReadoutMaskPreset(Base):
#     """
#     ReadoutThresholdPreset a preset of threshold values
#     """
#     __tablename__ = 'readout_masks'
#     id = Column(Integer, primary_key=True)
#     text_values = Column('values', String(1024))
#
#     board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
#     board = relationship("Board")
#
#     version = Column(Integer, default=_count_readout_masks)
#
#     @property
#     def values(self):
#         """
#         :return: list with pedestal values as strings
#         :rtype:  list
#         """
#         return str(self.text_values).split()
#
#     @values.setter
#     def values(self, values):
#         assert (isinstance(values, list))
#         self.text_values = list_to_db_text(values)
#
#     def _get_next_version(self):
#         return len(self.board.threshold_presets)
#
#     def __repr__(self):
#         return "<ReadoutMaskPreset id='{0}'>".format(self.id)
#
#
# #--------------------------------------------
# # class ReadoutThresholdPreset
# #--------------------------------------------
# class TriggerMaskPreset(Base):
#     """
#     ReadoutThresholdPreset a preset of threshold values
#     """
#     __tablename__ = 'trigger_masks'
#     id = Column(Integer, primary_key=True)
#     text_values = Column('values', String(1024))
#
#     board_id = Column(Integer, ForeignKey('boards.id'), nullable=False)
#     board = relationship("Board")
#
#     version = Column(Integer, default=_count_trigger_masks)
#
#     @property
#     def values(self):
#         """
#         :return: list with pedestal values as strings
#         :rtype:  list
#         """
#         return str(self.text_values).split()
#
#     @values.setter
#     def values(self, values):
#         assert (isinstance(values, list))
#         self.text_values = list_to_db_text(values)
#
#     def _get_next_version(self):
#         return len(self.board.threshold_presets)
#
#     def __repr__(self):
#         return "<TriggerMaskPreset id='{0}'>".format(self.id)
#
#
# #--------------------------------------------
# # class
# #--------------------------------------------
# class Daq(Base):
#     """
#
#     """
#     __tablename__ = 'daq'
#     id = Column(Integer, primary_key=True)
#
#     def __repr__(self):
#         return "<Daq id='{0}'>".format(self.id)
#
#
# #--------------------------------------------
# # class
# #--------------------------------------------
# class BoardConfiguration(Base):
#     """
#
#     """
#     __tablename__ = 'board_configurations'
#     id = Column(Integer, primary_key=True)
#     crate = Column(Integer, nullable=False, default=0)
#     slot = Column(Integer, nullable=False, default=0)
#     _readout_thresholds_id = Column("readout_thresholds_id", Integer, ForeignKey('readout_thresholds.id'), nullable=True)
#     _trigger_thresholds_id = Column("trigger_thresholds_id", Integer, ForeignKey('trigger_thresholds.id'), nullable=True)
#     _readout_masks_id = Column("readout_masks_id", Integer, ForeignKey('readout_masks.id'), nullable=True)
#     _trigger_masks_id = Column("trigger_masks_id", Integer, ForeignKey('trigger_masks.id'), nullable=True)
#     _dacs_id = Column("dacs_id", Integer, ForeignKey('dacs.id'), nullable=True)
#     _parameters_id = Column("board_parameters_id", Integer, ForeignKey('board_parameters.id'), nullable=True)
#
#     readout_threshold_preset = relationship("ReadoutThresholdPreset")
#     trigger_threshold_preset = relationship("TriggerThresholdPreset")
#     readout_mask_preset = relationship("ReadoutMaskPreset")
#     trigger_mask_preset = relationship("TriggerMaskPreset")
#     dac_preset = relationship("DacPreset")
#     parameter_preset = relationship("BoardParameterPreset")
#
#     board_id = Column(Integer, ForeignKey('boards.id'))
#     board = relationship("Board")
#     run_configs = relationship("RunConfiguration", secondary=_board_conf_has_run_conf_association)
#
#     def __repr__(self):
#         return "<BoardConfiguration id='{0}'>".format(self.id)


#--------------------------------------------
# class
#--------------------------------------------
class RunConfiguration(Base):
    """

    """
    __tablename__ = 'run_configurations'
    id = Column(Integer, primary_key=True)
    number = Column('run_number', Integer, primary_key=True)
    #board_configs = relationship("BoardConfiguration", secondary=_board_conf_has_run_conf_association)
    #board_installations = relationship("BoardInstallation", secondary=_board_inst_has_run_conf_association)
    files = relationship("ConfigurationFile", secondary=_files_has_run_conf_association,  back_populates="runs")
    #_trigger_config_id = Column('trigger_configuration_id', Integer, ForeignKey('trigger_configurations.id'), nullable=True)
    #trigger = relationship("TriggerConfiguration",  back_populates="runs")
    start_time = Column('started', DateTime, nullable=True)
    end_time = Column('finished', DateTime, nullable=True)
    records = relationship("RunRecord", back_populates="run")

    def __repr__(self):
        return "<RunConfiguration id='{0}'>".format(self.id)


#--------------------------------------------
# class
#--------------------------------------------
class ConfigurationFile(Base):
    """
    Table contains original coda and board configuration files
    """
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    sha256 = Column(String(44), nullable=False)
    content = Column(String(convert_unicode=True), nullable=False)
    description = Column(String(255), nullable=True)
    runs = relationship("RunConfiguration", secondary=_files_has_run_conf_association,  back_populates="files")

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
#     runs = relationship("RunConfiguration",  back_populates="trigger")
#
#     def __repr__(self):
#         return "<TriggerConfiguration id='{0}'>".format(self.id)
#

class RunRecord(Base):
    """
    RunInfo:
    Holds information attached to particular run. Such as start comments,
    end comments, statistics, etc...
    """
    __tablename__ = 'run_records'
    id = Column(Integer, primary_key=True)
    type = Column(String(255), nullable=False)
    format = Column("data_format", String(32), nullable=False, default="text")
    data = Column(String, nullable=False)
    actual_time = Column(DateTime, nullable=True)
    _run_conf_id = Column('run_configuration_id', Integer, ForeignKey('run_configurations.id'))
    run = relationship("RunConfiguration", back_populates="records")


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
    assert isinstance(values, {})
    return "; ".join([str(key)+"="+str(value) for key,value in sorted(values.items())])


def db_text_to_dic(value_str):
    """
    gets text of format "a=5; b=4" and returns a dictionary {"a":"5", "b":"4"}

    :return: {}
    >>>db_text_to_dic("a=5; b=4")
    {"a":"5", "b":"4"}
    """
    assert isinstance(value_str, str)
    tokens = filter(None, value_str.replace(" ",";").split(";"))   # gives like ['a=4', 'b=5.4']
    result = {}
    for token in tokens:
        key,value = token.split("=")
        result[key]=value
    return result


def db_text_to_float_dic(value_str):
    return { key:float(value) for key,value in db_text_to_dic(value_str).items()}


