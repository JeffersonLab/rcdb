sql_v1_to_v2 = """
CREATE TABLE IF NOT EXISTS `aliases` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `code` TEXT NOT NULL,
  `description` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS `rcdb`.`run_periods` (
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