import collections

__author__ = 'Dimitry Romanov'

import datetime
import posixpath

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import sessionmaker, reconstructor
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import desc

Base = declarative_base()

#This thing separates cells in data blob
blob_delimiter = "|"

# if cell of data table is a string and the string already contains blob_delimiter
# we have to encode blob_delimiter to blob_delimiter_replace on data write and decode it bach on data read
blob_delimiter_replacement = "&delimiter;"


def _count_threshold_presets(context):
    board_id =context.current_parameters["board_id"]
    result = context.engine.execute("select count(*) as n from threshold_presets where board_id=" + str(board_id))
    for row in result:
        context.current_parameters["version"] = int(row['n'])


def _count_pedestal_presets(context):
    board_id =context.current_parameters["board_id"]
    result = context.engine.execute("select count(*) as n from pedestal_presets where board_id=" + str(board_id))
    for row in result:
        context.current_parameters["version"] = int(row['n'])


def _count_baseline_presets(context):
    board_id =context.current_parameters["board_id"]
    result = context.engine.execute("select count(*) as n from baseline_presets where board_id=" + str(board_id))
    for row in result:
        context.current_parameters["version"] = int(row['n'])

_board_conf_has_run_conf_association = Table('board_configurations_has_run_configurations', Base.metadata,
    Column('board_configurations_id', Integer, ForeignKey('board_configurations.id')),
    Column('run_configurations_id', Integer, ForeignKey('run_configurations.id'))
)

#--------------------------------------------
# class Board
#--------------------------------------------
class Board(Base):
    """
    Represents trigger DB board.
    """
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True)
    board_name = Column('name',String(1024))
    serial = Column(String(512))
    board_type = Column(String(45))
    description = Column(String(1024))
    firmware = name = Column(String(45))
    modified = Column(DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)
    threshold_presets = relationship("ThresholdPreset", cascade="all, delete, delete-orphan")
    pedestal_presets = relationship("PedestalPreset", cascade="all, delete, delete-orphan")
    baseline_presets = relationship("BaselinePreset", cascade="all, delete, delete-orphan")
    configs = relationship("BoardConfiguration", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Board id='{0}' name='{1}'>".format(self.id, self.board_name)



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
    crait = Column(Integer,nullable=False, default=0)
    slot = Column(Integer,nullable=False, default=0)
    threshold_preset_id = Column("threshold_presets_id",Integer, ForeignKey('threshold_presets.id'))
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
    #_trigger_config_id = Column(Integer, ForeignKey('trigger_configurations.id'))
    #trigger_config = relationship("TriggerConfiguration")


    def __repr__(self):
        return "<RunConfiguration id='{0}'>".format(self.id)



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







#--------------------------------------------
# class Directory
#--------------------------------------------
class Directory(Base):
    """
    Represents CCDB directory object.
    Directories may contain other directories or TypeTable objects
    """
    __tablename__ = 'directories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    comment = Column(Text)
    created = Column(DateTime, default = datetime.datetime.now)
    modified = Column(DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)
    parent_id = Column('parentId', Integer)
    author_id = Column('authorId', Integer, default = 1)

    def __init__(self):
        self.path = ""
        self.parent_dir = None
        self.sub_dirs = []

    @reconstructor
    def on_load_init(self):
        self.path = ""
        self.parent_dir = None
        self.sub_dirs = []

    def __repr__(self):
        return "<Directory {0} '{1}'>".format(self.id, self.name)


#--------------------------------------------
# class TypeTable
#--------------------------------------------
class TypeTable(Base):
    __tablename__ = 'typeTables'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    comment = Column(Text)
    created = Column(DateTime, default = datetime.datetime.now)
    modified = Column(DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)
    parent_dir_id = Column('directoryId',Integer, ForeignKey('directories.id'))
    parent_dir = relationship("Directory", backref=backref('type_tables', order_by=id))
    constant_sets = relationship("ConstantSet", backref=backref('type_table'))
    columns = relationship("TypeTableColumn", order_by="TypeTableColumn.order", cascade="all, delete, delete-orphan", backref=backref("type_table") )
    rows_count = Column('nRows',Integer)
    _columns_count = Column('nColumns',Integer)
    author_id = Column('authorId', Integer, default = 1)

    @property
    def path(self):
        """
        :return: full path of the table
        :rtype: str
        """
        return posixpath.join(self.parent_dir.path, self.name)

    def __repr__(self):
        return "<TypeTable {0} '{1}'>".format(self.id, self.name)


#--------------------------------------------
# class TypeTableColumn
#--------------------------------------------
class TypeTableColumn(Base):
    __tablename__ = 'columns'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    comment = Column(Text)
    created = Column(DateTime, default = datetime.datetime.now)
    modified = Column(DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)
    order = Column(Integer)
    type = Column('columnType', Enum('int', 'uint','long','ulong','double','string','bool'))
    type_table_id = Column('typeId',Integer, ForeignKey('typeTables.id'))


    @property
    def path(self):
        return posixpath.join(self.parent_dir.path, self.name)

    def __repr__(self):
        return "<TypeTableColumn '{0}'>".format(self.name)


#--------------------------------------------
# class ConstantSet
#--------------------------------------------
class ConstantSet(Base):
    __tablename__ = 'constantSets'
    id = Column(Integer, primary_key=True)
    _vault = Column('vault', Text)
    created = Column(DateTime, default = datetime.datetime.now)
    modified = Column(DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)
    assignment = relationship("Assignment", uselist=False, back_populates="constant_set")
    type_table_id = Column('constantTypeId',Integer, ForeignKey('typeTables.id'))



    @property
    def vault(self):
        """
        Text-blob with data as it is presented in database
        :return: string with text-blob from db
        :rtype:  string
        """
        return self._vault


    def __repr__(self):
        return "<ConstantSet '{0}'>".format(self.id)


#--------------------------------------------
# class Assignment
#--------------------------------------------
class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default = datetime.datetime.now)
    modified = Column(DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)
    constant_set_id = Column('constantSetId', Integer, ForeignKey('constantSets.id'))
    constant_set = relationship("ConstantSet", uselist=False, back_populates="assignment")
    run_range_id = Column('runRangeId',Integer, ForeignKey('runRanges.id'))
    run_range = relationship("RunRange", backref=backref('assignments'))
    variation_id = Column('variationId',Integer, ForeignKey('variations.id'))
    variation = relationship("Variation", backref=backref('assignments'))
    _comment = Column('comment', Text)
    author_id = Column('authorId', Integer, default = 1)

    @property
    def comment(self):
        """
        returns comment for the object
        :rtype: basestring
        """
        return self._comment if self._comment is not None else ""

    @comment.setter
    def comment(self, value):
        self._comment = value

    @property
    def request(self):
        """
        Gets the unique "request" string in form of <path>:<run>:<variation>:<time>
        :rtype: basestring
        """

        path = self.constant_set.type_table.path
        run = self.run_range.min
        variation = self.variation.name
        time = self.modified.strftime("%Y-%m-%d_%H-%M-%S")

        return "{0}:{1}:{2}:{3}".format(path, run, variation, time)


    def __repr__(self):
        return "<Assignment '{0}'>".format(self.id)

    def print_deps(self):
        print " ASSIGNMENT: " + repr(self) \
              + " TABLE: " + repr (self.constant_set.type_table)\
              + " RUN RANGE: " + repr(self.run_range)\
              + " VARIATION: " + repr(self.variation)\
              + " SET: " + repr (self.constant_set)
        print "      |"
        print "      +-->" + repr(self.constant_set.vault)
        print "      +-->" + repr(self.constant_set.data_list)
        print "      +-->" + repr(self.constant_set.data_table)


#--------------------------------------------
# class RunRange
#--------------------------------------------
class RunRange(Base):
    __tablename__ = 'runRanges'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created = Column(DateTime, default = datetime.datetime.now)
    modified = Column(DateTime, default = datetime.datetime.now, onupdate = datetime.datetime.now)
    comment = Column(Text)
    min = Column('runMin',Integer)
    max = Column('runMax',Integer)

    def __repr__(self):
        if self.name != "":
            return "<RunRange {0} {3}:{1}-{2}>".format(self.id, self.min, self.max, self.name)
        else:
            return "<RunRange {0} '{1}-{2}'>".format(self.id, self.min, self.max)


#--------------------------------------------
# class Variation
#--------------------------------------------
class Variation(Base):
    __tablename__ = 'variations'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created = Column(DateTime, default = datetime.datetime.now)
    comment = Column(Text)
    author_id = Column('authorId', Integer, default = 1)

    def __repr__(self):
        return "<Variation {0} '{1}'>".format(self.id, self.name)


#--------------------------------------------
# class User
#--------------------------------------------
class User(Base):
    """
    Represent user of the ccdb. Used for logging and authentication
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    created = Column('created', DateTime, default = datetime.datetime.now)
    last_action_time = Column('lastActionTime', DateTime)#, nullable=False
    name = Column(String(100), nullable=False)
    password = Column(String(100), nullable=True)
    _roles_str = Column('roles', String, nullable=False)
    name = Column(String(100), nullable=False)
    info  = Column(String(125), nullable=False)

    @property
    def roles(self):
        """
        Returns a list of user roles
        :rtype:[]
        """
        return self._roles_str.split(",")

    @roles.setter
    def roles(self, value):
        self._roles_str = ",".join(value)


#--------------------------------------------
# class LogRecord - record logs
#--------------------------------------------
class LogRecord(Base):
    """
    One record to the log
    """
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, nullable=False)
    created = Column('created', DateTime, default = datetime.datetime.now)
    affected_ids = Column('affectedIds', String)#, nullable=False
    action = Column(String(7), nullable=False)
    description = Column(String(255), nullable=False)
    comment = Column(String, nullable=True)
    author_id = Column('authorId', Integer, ForeignKey('users.id'))
    author = relationship("User")

#--------------------------------------------
# function Connect to the database
#--------------------------------------------
def connect(connection_string="mysql+mysqlconnector://triggerdb@127.0.0.1/triggerdb"):
    """
    Connects to the database and returns SQL alchemy session object
    that allows to manipulate objects from database

    :param connection_string: Connection string that specifies database type, user, server, etc.
                              By default it is mysql://triggerdb@127.0.0.1/triggerdb
    :return: SQLAlchemy session
    """
    engine = sqlalchemy.create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    return Session()


class database(object):

    def __init__(self):
        self.session = None

    def connect(self,connection_string="mysql://triggerdb@127.0.0.1/triggerdb"):
        """
        Connects to the database and returns SQL alchemy session object
        that allows to manipulate objects from database

        :param connection_string: Connection string that specifies database type, user, server, etc.
                                  By default it is mysql://triggerdb@127.0.0.1/triggerdb
        :return: SQLAlchemy session
        """
        engine = sqlalchemy.create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        return self.session




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

def make_threshold_preset(db, board, values):
    """
    checks if values
    :param values:
    :return:
    """

    if isinstance(values, list):
        text_values = list_to_db_text(values)




if __name__=="__main__":
    engine = sqlalchemy.create_engine('mysql+mysqlconnector://triggerdb@127.0.0.1/triggerdb')
    Session = sessionmaker(bind=engine)
    session = Session()
    boards = session.query(Board).all()




    """
        print sqlalchemy.__version__

        root_dir = Directory()
        root_dir.path = '/'
        root_dir.name = ''
        root_dir.id = 0

        engine = sqlalchemy.create_engine('mysql://ccdb_user@127.0.0.1/ccdb')

        def structure_dirs(dirs):

            assert(isinstance(dirs,type({})))

            #clear the full path dictionary
            dirsByFullPath = {root_dir.path: root_dir}

            #begin loop through the directories
            for dir in dirs.values():
                assert (isinstance(dir, Directory))

                parent_dir = root_dir

                # and check if it have parent directory
                if dir.parent_id >0:
                    #this directory must have a parent! so now search it
                    parent_dir = dirs[dir.parent_id]

                parent_dir.sub_dirs.append(dir)
                dir.path = posixpath.join(parent_dir.path, dir.name)
                dir.parent_dir = parent_dir
                dirsByFullPath[dir.path] = dir

            return dirsByFullPath
            #end of structure_dirs()


        def get_dirs_by_id_dic(dirs):
            result = {}
            for dir in dirs:
                assert(isinstance(dir, Directory))
                result[dir.id]=dir

            return result


        Session = sessionmaker(bind=engine)
        session = Session()
        dirsById = get_dirs_by_id_dic(session.query(Directory))
        dirsByFullPath = structure_dirs(dirsById)


        for key,val in dirsByFullPath.items():
                print key, val, val.id

        experiment_dir = dirsByFullPath['/test/test_vars']

        assert (isinstance(experiment_dir, Directory))

        t = TypeTable()

        for table in experiment_dir.type_tables:
            print " TABLE: " + table.name
            print " +--> COLUMNS:"

            for column in table.columns:
                print "      +-->" + column.name

            print " +--> CONSTANTS:"

            for set in table.constant_sets:
                print "      +-->" + set.vault


        #assignments = session.query(Assignment)

        #for assignment in assignments:
         #   assignment.print_deps()

        query = session.query(Assignment).join(ConstantSet).join(TypeTable).join(RunRange).join(Variation)\
                .filter(Variation.name == "default").filter(TypeTable.name=="test_table").filter(RunRange.min<=1000).filter(RunRange.max>=1000)\
                .order_by(desc(Assignment.id)).limit(1).one()

        print query

        print query.print_deps()

        #for assignment in query:
        #    assignment.print_deps()
        print session.dirty

        q = session.query(Directory)
        q = q.limit(1)

        print q"""
