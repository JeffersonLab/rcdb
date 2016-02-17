import rcdb


def create_memory_sqlite():
    """
    :return: ConfigurationProvider connected to memory sqlite database
    """
    db = rcdb.ConfigurationProvider("sqlite://")
    rcdb.model.Base.metadata.create_all(db.engine)
    return db
