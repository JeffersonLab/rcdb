SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `trigger_db` ;
CREATE SCHEMA IF NOT EXISTS `trigger_db` DEFAULT CHARACTER SET latin1 ;
USE `trigger_db` ;

-- -----------------------------------------------------
-- Table `runconf_db`.`boards`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`boards` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`boards` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `board_type` VARCHAR(45) NOT NULL ,
  `name` VARCHAR(1024) NOT NULL ,
  `serial` VARCHAR(512) NOT NULL ,
  `description` VARCHAR(1024) NULL ,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
  `firmware` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`pedestal_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`pedestal_presets` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`pedestal_presets` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `values` VARCHAR(1045) NOT NULL ,
  `version` INT NOT NULL ,
  `board_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_pedestals_boards1_idx` (`board_id` ASC) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  CONSTRAINT `fk_pedestals_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `trigger_db`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`baseline_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`baseline_presets` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`baseline_presets` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `version` INT NOT NULL ,
  `values` VARCHAR(1024) NOT NULL ,
  `board_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_base_lines_boards1_idx` (`board_id` ASC) ,
  CONSTRAINT `fk_base_lines_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `trigger_db`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`trigger_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`trigger_configurations` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`trigger_configurations` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `type` VARCHAR(45) NOT NULL ,
  `parameters` INT NULL ,
  `prescale` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`daq`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`daq` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`daq` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `readout_mode` VARCHAR(45) NULL ,
  `window_size` INT NULL ,
  `nsa_nsb` VARCHAR(45) NULL ,
  `pulses_num` VARCHAR(45) NULL ,
  `block_readout` VARCHAR(45) NULL ,
  `loob_back` VARCHAR(45) NULL ,
  `chanel_mask` INT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`run_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`run_configurations` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`run_configurations` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `run_number` INT UNSIGNED NOT NULL DEFAULT 0 ,
  `trigger_configurations_id` INT NOT NULL ,
  `daq_id` INT NOT NULL ,
  `started` DATETIME NULL ,
  `finished` DATETIME NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  INDEX `fk_run_configurations_trigger_configurations1_idx` (`trigger_configurations_id` ASC) ,
  INDEX `fk_run_configurations_daq1_idx` (`daq_id` ASC) ,
  CONSTRAINT `fk_run_configurations_trigger_configurations1`
    FOREIGN KEY (`trigger_configurations_id` )
    REFERENCES `trigger_db`.`trigger_configurations` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_run_configurations_daq1`
    FOREIGN KEY (`daq_id` )
    REFERENCES `trigger_db`.`daq` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`threshold_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`threshold_presets` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`threshold_presets` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `version` INT NOT NULL ,
  `values` VARCHAR(1024) NOT NULL ,
  `board_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC) ,
  CONSTRAINT `fk_thresholds_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `trigger_db`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`board_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`board_configurations` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`board_configurations` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `board_id` INT NOT NULL ,
  `crate` INT NOT NULL DEFAULT 0 ,
  `slot` INT NOT NULL DEFAULT 0 ,
  `threshold_presets_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_boards_configuration_boards1_idx` (`board_id` ASC) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  INDEX `fk_board_configurations_threshold_presets1_idx` (`threshold_presets_id` ASC) ,
  CONSTRAINT `fk_boards_configuration_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `trigger_db`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_threshold_presets1`
    FOREIGN KEY (`threshold_presets_id` )
    REFERENCES `trigger_db`.`threshold_presets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`board_configurations_has_run_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`board_configurations_has_run_configurations` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`board_configurations_has_run_configurations` (
  `board_configurations_id` INT NOT NULL ,
  `run_configurations_id` INT NOT NULL ,
  PRIMARY KEY (`board_configurations_id`, `run_configurations_id`) ,
  INDEX `fk_board_configurations_has_run_configurations_run_configur_idx` (`run_configurations_id` ASC) ,
  INDEX `fk_board_configurations_has_run_configurations_board_config_idx` (`board_configurations_id` ASC) ,
  CONSTRAINT `fk_board_configurations_has_run_configurations_board_configur1`
    FOREIGN KEY (`board_configurations_id` )
    REFERENCES `trigger_db`.`board_configurations` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_has_run_configurations_run_configurat1`
    FOREIGN KEY (`run_configurations_id` )
    REFERENCES `trigger_db`.`run_configurations` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`configuration_files`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `trigger_db`.`configuration_files` ;

CREATE  TABLE IF NOT EXISTS `trigger_db`.`configuration_files` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `run_configurations_id` INT NOT NULL ,
  `path` TEXT NOT NULL ,
  `sha256` VARCHAR(44) NOT NULL ,
  `content` LONGTEXT NULL ,
  `description` VARCHAR(255) NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_run_files_run_configurations1_idx` (`run_configurations_id` ASC) ,
  CONSTRAINT `fk_run_files_run_configurations1`
    FOREIGN KEY (`run_configurations_id` )
    REFERENCES `trigger_db`.`run_configurations` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'Table contains original coda and board configuration files';

USE `trigger_db` ;

SET SQL_MODE = '';
GRANT USAGE ON *.* TO trigger_db;
 DROP USER trigger_db;
SET SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';
CREATE USER 'trigger_db';

GRANT ALL ON TABLE trigger_db.* TO 'trigger_db';

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`boards`
-- -----------------------------------------------------
START TRANSACTION;
USE `trigger_db`;
INSERT INTO `trigger_db`.`boards` (`id`, `board_type`, `name`, `serial`, `description`, `modified`, `firmware`) VALUES (1, 'FADC', 'test_one', '11', 'test board one', NULL, NULL);
INSERT INTO `trigger_db`.`boards` (`id`, `board_type`, `name`, `serial`, `description`, `modified`, `firmware`) VALUES (2, 'FADC', 'test_two', '12', 'test board two', NULL, NULL);

COMMIT;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`pedestal_presets`
-- -----------------------------------------------------
START TRANSACTION;
USE `trigger_db`;
INSERT INTO `trigger_db`.`pedestal_presets` (`id`, `values`, `version`, `board_id`) VALUES (1, '10 20 30 40 50 60 70 80 90 100 110 120 130 140 150 160', 0, 1);
INSERT INTO `trigger_db`.`pedestal_presets` (`id`, `values`, `version`, `board_id`) VALUES (2, '1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6', 1, 1);
INSERT INTO `trigger_db`.`pedestal_presets` (`id`, `values`, `version`, `board_id`) VALUES (3, '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0', 0, 2);

COMMIT;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`baseline_presets`
-- -----------------------------------------------------
START TRANSACTION;
USE `trigger_db`;
INSERT INTO `trigger_db`.`baseline_presets` (`id`, `version`, `values`, `board_id`) VALUES (1, 0, '1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1', 1);
INSERT INTO `trigger_db`.`baseline_presets` (`id`, `version`, `values`, `board_id`) VALUES (2, 1, '2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2', 1);
INSERT INTO `trigger_db`.`baseline_presets` (`id`, `version`, `values`, `board_id`) VALUES (3, 0, '1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6', 2);

COMMIT;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`trigger_configurations`
-- -----------------------------------------------------
START TRANSACTION;
USE `trigger_db`;
INSERT INTO `trigger_db`.`trigger_configurations` (`id`, `type`, `parameters`, `prescale`) VALUES (1, 'ASD', 1, '1 2 3');

COMMIT;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`daq`
-- -----------------------------------------------------
START TRANSACTION;
USE `trigger_db`;
INSERT INTO `trigger_db`.`daq` (`id`, `readout_mode`, `window_size`, `nsa_nsb`, `pulses_num`, `block_readout`, `loob_back`, `chanel_mask`) VALUES (1, 'asd', 1, 'asd', 'asd', 'asd', '123', 255);

COMMIT;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`run_configurations`
-- -----------------------------------------------------
START TRANSACTION;
USE `trigger_db`;
INSERT INTO `trigger_db`.`run_configurations` (`id`, `run_number`, `trigger_configurations_id`, `daq_id`, `started`, `finished`) VALUES (1, 1000, 1, 1, NULL, NULL);

COMMIT;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`threshold_presets`
-- -----------------------------------------------------
START TRANSACTION;
USE `trigger_db`;
INSERT INTO `trigger_db`.`threshold_presets` (`id`, `version`, `values`, `board_id`) VALUES (1, 0, '1.01 1.02 1.03 1.04 1.1 1.11 1.12 1.13 2.0 2.1 2.3 5.123 6.123 16.123 1.01', 1);
INSERT INTO `trigger_db`.`threshold_presets` (`id`, `version`, `values`, `board_id`) VALUES (2, 1, '1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 ', 1);
INSERT INTO `trigger_db`.`threshold_presets` (`id`, `version`, `values`, `board_id`) VALUES (3, 0, '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ', 2);

COMMIT;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`board_configurations`
-- -----------------------------------------------------
START TRANSACTION;
USE `trigger_db`;
INSERT INTO `trigger_db`.`board_configurations` (`id`, `board_id`, `crate`, `slot`, `threshold_presets_id`) VALUES (1, 1, 5, 5, 1);
INSERT INTO `trigger_db`.`board_configurations` (`id`, `board_id`, `crate`, `slot`, `threshold_presets_id`) VALUES (2, 2, 5, 6, 3);

COMMIT;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`board_configurations_has_run_configurations`
-- -----------------------------------------------------
START TRANSACTION;
USE `trigger_db`;
INSERT INTO `trigger_db`.`board_configurations_has_run_configurations` (`board_configurations_id`, `run_configurations_id`) VALUES (1, 1);

COMMIT;
