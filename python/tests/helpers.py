import rcdb


def create_memory_sqlite():
    """
    :return: ConfigurationProvider connected to memory sqlite database
    """
    db = rcdb.ConfigurationProvider("sqlite://", check_version=False)
    rcdb.provider.destroy_all_create_schema(db)
    return db
