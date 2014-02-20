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


def _count_threshold_presets(context):
    board_id = context.current_parameters["board_id"]
    result = context.engine.execute("SELECT count(*) AS n FROM threshold_presets WHERE board_id=?", board_id)
    for row in result:
        context.current_parameters["version"] = int(row['n'])


def _count_pedestal_presets(context):
    board_id = context.current_parameters["board_id"]
    result = context.engine.execute("SELECT count(*) AS n FROM pedestal_presets WHERE board_id=?", board_id)
    for row in result:
        context.current_parameters["version"] = int(row['n'])


def _count_baseline_presets(context):
    board_id = context.current_parameters["board_id"]
    result = context.engine.execute("SELECT count(*) AS n FROM baseline_presets WHERE board_id=?", board_id)
    for row in result:
        context.current_parameters["version"] = int(row['n'])


_board_conf_has_run_conf_association = Table('board_configurations_has_run_configurations', Base.metadata,
                                             Column('board_configurations_id', Integer,
                                                    ForeignKey('board_configurations.id')),
                                             Column('run_configurations_id', Integer,
                                                    ForeignKey('run_configurations.id')))


_board_inst_has_run_conf_association = Table('board_installations_has_run_configurations', Base.metadata,
                                             Column('board_installations_id', Integer,
                                                    ForeignKey('board_installations.id')),
                                             Column('run_configurations_id', Integer,
                                                    ForeignKey('run_configurations.id')))


#--------------------------------------------
# class Board
#--------------------------------------------
class Board(Base):
    """
    Represents trigger DB board.
    """
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True)
    board_name = Column('name', String(1024))
    serial = Column(String(512))
    board_type = Column(String(45))
    description = Column(String(1024))
    firmware = Column(String(45))
    modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    threshold_presets = relationship("ThresholdPreset", cascade="all, delete, delete-orphan")
    pedestal_presets = relationship("PedestalPreset", cascade="all, delete, delete-orphan")
    baseline_presets = relationship("BaselinePreset", cascade="all, delete, delete-orphan")
    configs = relationship("BoardConfiguration", cascade="all, delete, delete-orphan")
    installations = relationship("BoardInstallation", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Board id='{0}' name='{1}'>".format(self.id, self.board_name)


#--------------------------------------------
# class Crate
#--------------------------------------------
class Crate(Base):
    """
    Represents Crate where boards are placed
    """
    __tablename__ = 'crates'
    id = Column(Integer, primary_key=True)
    name = Column('rock_name', String(45))
    installations = relationship("BoardInstallation", cascade="all, delete, delete-orphan")


#--------------------------------------------
# class BoardInstallation
#--------------------------------------------
class BoardInstallation(Base):
    """
    Represents board installation
    """
    __tablename__ = 'board_installations'
    id = Column(Integer, primary_key=True)

    board_id = Column(Integer, ForeignKey('boards.id'))
    board = relationship("Board")
    crate_id = Column(Integer, ForeignKey('crates.id'))
    crate = relationship("Crate")
    run_configs = relationship("RunConfiguration", secondary=_board_inst_has_run_conf_association)




#--------------------------------------------
# class ThresholdPreset
#--------------------------------------------
class ThresholdPreset(Base):
    """
    Represent a preset of threshold values
    """
    __tablename__ = 'threshold_presets'
    id = Column(Integer, primary_key=True)
    text_values = Column('values', String(1024))

    board_id = Column(Integer, ForeignKey('boards.id'))
    board = relationship("Board")

    version = Column(Integer, default=_count_threshold_presets)

    @property
    def values(self):
        """
        :return: list with pedestal values as strings
        :rtype:  list
        """
        return self.text_values.split()

    @values.setter
    def values(self, values):
        assert (isinstance(values, list))
        self.text_values = list_to_db_text(values)

    def _get_next_version(self):
        return len(self.board.threshold_presets)

    def __repr__(self):
        return "<ThresholdPreset id='{0}'>".format(self.id)


#--------------------------------------------
# class PedestalPreset
#--------------------------------------------
class PedestalPreset(Base):
    """
    Represent a preset of pedestal values
    """
    __tablename__ = 'pedestal_presets'
    id = Column(Integer, primary_key=True)
    text_values = Column('values', String(1024))
    board_id = Column(Integer, ForeignKey('boards.id'))
    board = relationship("Board")
    version = Column(Integer, default=_count_pedestal_presets)

    @property
    def values(self):
        """
        :return: list with pedestal values
        :rtype:  list
        """
        return self.text_values.split()

    @values.setter
    def values(self, values):
        assert (isinstance(values, list))
        self.text_values = list_to_db_text(values)

    def __repr__(self):
        return "<PedestalPreset id='{0}'>".format(self.id)


#--------------------------------------------
# class PedestalPreset
#--------------------------------------------
class BaselinePreset(Base):
    """
    Represent a preset of pedestal values
    """
    __tablename__ = 'baseline_presets'
    id = Column(Integer, primary_key=True)
    text_values = Column('values', String(1024))
    board_id = Column(Integer, ForeignKey('boards.id'))
    board = relationship("Board")
    version = Column(Integer, default=_count_baseline_presets)

    @property
    def values(self):
        """
        :return: list with pedestal values
        :rtype:  list
        """
        return self.text_values.split()

    @values.setter
    def values(self, values):
        assert (isinstance(values, list))
        self.text_values = list_to_db_text(values)

    def __repr__(self):
        return "<BaseLinePreset id='{0}'>".format(self.id)


#--------------------------------------------
# class
#--------------------------------------------
class Daq(Base):
    """

    """
    __tablename__ = 'daq'
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<Daq id='{0}'>".format(self.id)


#--------------------------------------------
# class
#--------------------------------------------
class BoardConfiguration(Base):
    """

    """
    __tablename__ = 'board_configurations'
    id = Column(Integer, primary_key=True)
    crate = Column(Integer, nullable=False, default=0)
    slot = Column(Integer, nullable=False, default=0)
    threshold_preset_id = Column("threshold_presets_id", Integer, ForeignKey('threshold_presets.id'))
    threshold_preset = relationship("ThresholdPreset")
    board_id = Column(Integer, ForeignKey('boards.id'))
    board = relationship("Board")
    run_configs = relationship("RunConfiguration", secondary=_board_conf_has_run_conf_association)

    def __repr__(self):
        return "<BoardConfiguration id='{0}'>".format(self.id)


#--------------------------------------------
# class
#--------------------------------------------
class RunConfiguration(Base):
    """

    """
    __tablename__ = 'run_configurations'
    id = Column(Integer, primary_key=True)
    number = Column('run_number', Integer, primary_key=True)
    board_configs = relationship("BoardConfiguration", secondary=_board_conf_has_run_conf_association)
    board_installations = relationship("BoardInstallation", secondary=_board_inst_has_run_conf_association)
    configuration_files = relationship("ConfigurationFile", cascade="all, delete, delete-orphan")
    #_trigger_config_id = Column(Integer, ForeignKey('trigger_configurations.id'))
    #trigger_config = relationship("TriggerConfiguration")

    def __repr__(self):
        return "<RunConfiguration id='{0}'>".format(self.id)


#--------------------------------------------
# class
#--------------------------------------------
class ConfigurationFile(Base):
    """
    Table contains original coda and board configuration files
    """
    __tablename__ = 'configuration_files'
    id = Column(Integer, primary_key=True)
    run_configuration_id = Column("run_configurations_id", Integer, ForeignKey('run_configurations.id'))
    run_configuration = relationship("RunConfiguration")
    path = Column(String, nullable=False)
    sha256 = Column(String(44), nullable=False)
    content = Column(UnicodeText, nullable=False)
    description = Column(String(255), nullable=True)


#--------------------------------------------
# class
#--------------------------------------------
class TriggerConfiguration(Base):
    """

    """
    __tablename__ = 'trigger_configurations'
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return "<TriggerConfiguration id='{0}'>".format(self.id)


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