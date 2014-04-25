import sqlalchemy
from sqlalchemy.orm import sessionmaker
#from .model import Board
from .provider import ConfigurationProvider
from constants import START_COMMENT_RECORD_KEY, END_COMMENT_RECORD_KEY, COMPONENT_STAT_KEY, FADC250_KEY


#This thing separates cells in data blob
blob_delimiter = "|"

# if cell of data table is a string and the string already contains blob_delimiter
# we have to encode blob_delimiter to blob_delimiter_replace on data write and decode it bach on data read
blob_delimiter_replacement = "&delimiter;"


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



if __name__ == "__main__":
    engine = sqlalchemy.create_engine('mysql+mysqlconnector://triggerdb@127.0.0.1/triggerdb')
    Session = sessionmaker(bind=engine)
    session = Session()
    #boards = session.query(Board).all()




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

