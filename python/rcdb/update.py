from rcdb.model import SchemaVersion, Alias, RunPeriod

mysql_v1_to_v2 = """
CREATE TABLE IF NOT EXISTS `aliases` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `code` TEXT NOT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `run_periods` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  `start_date` DATE NULL DEFAULT NULL,
  `end_date` DATE NULL DEFAULT NULL,
  `run_min` INT(11) NOT NULL,
  `run_max` INT(11) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;
"""

def update_v1(provider):
    """Update DB from V1 to V2"""

    import rcdb
    from rcdb.provider import stamp_schema_version

    # V2 differs from V1 only by 2 new tables. Create them
    rcdb.model.Base.metadata.create_all(provider.engine, tables=[Alias.__table__, RunPeriod.__table__])
    version = stamp_schema_version(provider)

