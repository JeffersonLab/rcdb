SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `runconf_db` ;
CREATE SCHEMA IF NOT EXISTS `runconf_db` DEFAULT CHARACTER SET latin1 ;
USE `runconf_db` ;

-- -----------------------------------------------------
-- Table `runconf_db`.`boards`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`boards` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`boards` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `board_type` VARCHAR(45) NOT NULL,
  `serial` VARCHAR(512) NOT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`trigger_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`trigger_configurations` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`trigger_configurations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(45) NOT NULL,
  `parameters` TEXT NULL,
  `prescale` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`run_parameters`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`run_parameters` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`run_parameters` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `fadc_readout_mode` VARCHAR(45) NULL,
  `fadc_window_size` VARCHAR(45) NULL,
  `nsa_nsb` VARCHAR(45) NULL,
  `pulses_num` VARCHAR(45) NULL,
  `block_readout` VARCHAR(45) NULL,
  `loob_back` VARCHAR(45) NULL,
  `chanel_mask` INT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`run_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`run_configurations` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`run_configurations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `run_number` INT UNSIGNED NOT NULL DEFAULT 0,
  `trigger_configuration_id` INT NULL,
  `daq_id` INT NULL DEFAULT 1,
  `started` DATETIME NULL DEFAULT NULL,
  `finished` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `fk_run_configurations_trigger_configurations1_idx` (`trigger_configuration_id` ASC),
  INDEX `fk_run_configurations_daq1_idx` (`daq_id` ASC),
  CONSTRAINT `fk_run_configurations_trigger_configurations1`
    FOREIGN KEY (`trigger_configuration_id`)
    REFERENCES `runconf_db`.`trigger_configurations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_run_configurations_daq1`
    FOREIGN KEY (`daq_id`)
    REFERENCES `runconf_db`.`run_parameters` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`readout_mask_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`readout_mask_presets` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`readout_mask_presets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards1`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`trigger_mask_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`trigger_mask_presets` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`trigger_mask_presets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards10`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`readout_threshold_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`readout_threshold_presets` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`readout_threshold_presets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards11`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`trigger_threshold_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`trigger_threshold_presets` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`trigger_threshold_presets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards110`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`trigger_baseline_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`trigger_baseline_presets` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`trigger_baseline_presets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards1100`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`readout_baseline_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`readout_baseline_presets` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`readout_baseline_presets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards101`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`dac_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`dac_presets` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`dac_presets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards100`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`board_parameter_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`board_parameter_presets` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`board_parameter_presets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards1010`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`board_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`board_configurations` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`board_configurations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `board_id` INT NOT NULL,
  `dac_preset_id` INT NULL,
  `readout_mask_id` INT NULL,
  `trigger_mask_id` INT NULL,
  `readout_threshold_id` INT NULL,
  `trigger_threshold_id` INT NULL,
  `trigger_baseline_id` INT NULL,
  `readout_baseline_id` INT NULL,
  `board_parameter_id` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_boards_configuration_boards1_idx` (`board_id` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `fk_board_configurations_threshold_presets1_idx` (`readout_mask_id` ASC),
  INDEX `fk_board_configurations_trigger_masks1_idx` (`trigger_mask_id` ASC),
  INDEX `fk_board_configurations_readout_thresholds1_idx` (`readout_threshold_id` ASC),
  INDEX `fk_board_configurations_trigger_thresholds1_idx` (`trigger_threshold_id` ASC),
  INDEX `fk_board_configurations_trigger_baselines1_idx` (`trigger_baseline_id` ASC),
  INDEX `fk_board_configurations_readout_baselines1_idx` (`readout_baseline_id` ASC),
  INDEX `fk_board_configurations_dacs1_idx` (`dac_preset_id` ASC),
  INDEX `fk_board_configurations_board_parameters1_idx` (`board_parameter_id` ASC),
  CONSTRAINT `fk_boards_configuration_boards1`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_threshold_presets1`
    FOREIGN KEY (`readout_mask_id`)
    REFERENCES `runconf_db`.`readout_mask_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_trigger_masks1`
    FOREIGN KEY (`trigger_mask_id`)
    REFERENCES `runconf_db`.`trigger_mask_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_readout_thresholds1`
    FOREIGN KEY (`readout_threshold_id`)
    REFERENCES `runconf_db`.`readout_threshold_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_trigger_thresholds1`
    FOREIGN KEY (`trigger_threshold_id`)
    REFERENCES `runconf_db`.`trigger_threshold_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_trigger_baselines1`
    FOREIGN KEY (`trigger_baseline_id`)
    REFERENCES `runconf_db`.`trigger_baseline_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_readout_baselines1`
    FOREIGN KEY (`readout_baseline_id`)
    REFERENCES `runconf_db`.`readout_baseline_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_dacs1`
    FOREIGN KEY (`dac_preset_id`)
    REFERENCES `runconf_db`.`dac_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_board_parameters1`
    FOREIGN KEY (`board_parameter_id`)
    REFERENCES `runconf_db`.`board_parameter_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`board_configurations_has_run_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`board_configurations_has_run_configurations` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`board_configurations_has_run_configurations` (
  `board_configuration_id` INT NOT NULL,
  `run_configuration_id` INT NOT NULL,
  PRIMARY KEY (`board_configuration_id`, `run_configuration_id`),
  INDEX `fk_board_configurations_has_run_configurations_run_configur_idx` (`run_configuration_id` ASC),
  INDEX `fk_board_configurations_has_run_configurations_board_config_idx` (`board_configuration_id` ASC),
  CONSTRAINT `fk_board_configurations_has_run_configurations_board_configur1`
    FOREIGN KEY (`board_configuration_id`)
    REFERENCES `runconf_db`.`board_configurations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_has_run_configurations_run_configurat1`
    FOREIGN KEY (`run_configuration_id`)
    REFERENCES `runconf_db`.`run_configurations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
PACK_KEYS = DEFAULT;


-- -----------------------------------------------------
-- Table `runconf_db`.`files`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`files` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`files` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `path` TEXT NOT NULL,
  `sha256` VARCHAR(44) NOT NULL,
  `content` LONGTEXT NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'Table contains original coda and board configuration files';


-- -----------------------------------------------------
-- Table `runconf_db`.`crates`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`crates` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`crates` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`board_installations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`board_installations` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`board_installations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `slot` INT NOT NULL DEFAULT 0,
  `board_id` INT NOT NULL,
  `crate_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_boards_configuration_boards1_idx` (`board_id` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `fk_board_configurations_crates1_idx` (`crate_id` ASC),
  CONSTRAINT `fk_boards_configuration_boards10`
    FOREIGN KEY (`board_id`)
    REFERENCES `runconf_db`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_crates10`
    FOREIGN KEY (`crate_id`)
    REFERENCES `runconf_db`.`crates` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`board_installations_has_run_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`board_installations_has_run_configurations` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`board_installations_has_run_configurations` (
  `board_installation_id` INT NOT NULL,
  `run_configuration_id` INT NOT NULL,
  PRIMARY KEY (`board_installation_id`, `run_configuration_id`),
  INDEX `fk_table1_board_installations1_idx` (`board_installation_id` ASC),
  INDEX `fk_table1_run_configurations1_idx` (`run_configuration_id` ASC),
  CONSTRAINT `fk_table1_board_installations1`
    FOREIGN KEY (`board_installation_id`)
    REFERENCES `runconf_db`.`board_installations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_table1_run_configurations1`
    FOREIGN KEY (`run_configuration_id`)
    REFERENCES `runconf_db`.`run_configurations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`files_has_run_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`files_has_run_configurations` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`files_has_run_configurations` (
  `run_configuration_id` INT NOT NULL,
  `file_id` INT NOT NULL,
  PRIMARY KEY (`run_configuration_id`, `file_id`),
  INDEX `fk_files_has_run_configuration_files1_idx` (`file_id` ASC),
  CONSTRAINT `fk_files_has_run_configuration_run_configurations1`
    FOREIGN KEY (`run_configuration_id`)
    REFERENCES `runconf_db`.`run_configurations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_files_has_run_configuration_files1`
    FOREIGN KEY (`file_id`)
    REFERENCES `runconf_db`.`files` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`run_records`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`run_records` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`run_records` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `key` VARCHAR(255) NOT NULL,
  `value` LONGTEXT NOT NULL,
  `value_type` VARCHAR(32) NOT NULL DEFAULT 'text',
  `actual_time` DATETIME NOT NULL,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `run_configuration_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `fk_run_info_run_configurations1_idx` (`run_configuration_id` ASC),
  CONSTRAINT `fk_run_info_run_configurations1`
    FOREIGN KEY (`run_configuration_id`)
    REFERENCES `runconf_db`.`run_configurations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `runconf_db`.`logs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `runconf_db`.`logs` ;

CREATE TABLE IF NOT EXISTS `runconf_db`.`logs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `table_ids` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
ENGINE = InnoDB;

SET SQL_MODE = '';
GRANT USAGE ON *.* TO runconf_db;
 DROP USER runconf_db;
SET SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';
CREATE USER 'runconf_db';

GRANT ALL ON TABLE trigger_db.* TO 'runconf_db';

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `runconf_db`.`boards`
-- -----------------------------------------------------
START TRANSACTION;
USE `runconf_db`;
INSERT INTO `runconf_db`.`boards` (`id`, `board_type`, `serial`, `modified`) VALUES (1, 'FADC', '11', NULL);
INSERT INTO `runconf_db`.`boards` (`id`, `board_type`, `serial`, `modified`) VALUES (2, 'FADC', '12', NULL);

COMMIT;


-- -----------------------------------------------------
-- Data for table `runconf_db`.`trigger_configurations`
-- -----------------------------------------------------
START TRANSACTION;
USE `runconf_db`;
INSERT INTO `runconf_db`.`trigger_configurations` (`id`, `type`, `parameters`, `prescale`) VALUES (1, 'unknown', '1', '1 2 3');
INSERT INTO `runconf_db`.`trigger_configurations` (`id`, `type`, `parameters`, `prescale`) VALUES (2, 'test', '2', '1 2 3');

COMMIT;


-- -----------------------------------------------------
-- Data for table `runconf_db`.`run_parameters`
-- -----------------------------------------------------
START TRANSACTION;
USE `runconf_db`;
INSERT INTO `runconf_db`.`run_parameters` (`id`, `fadc_readout_mode`, `fadc_window_size`, `nsa_nsb`, `pulses_num`, `block_readout`, `loob_back`, `chanel_mask`) VALUES (1, 'asd', '1', 'asd', 'asd', 'asd', '123', 255);

COMMIT;


-- -----------------------------------------------------
-- Data for table `runconf_db`.`run_configurations`
-- -----------------------------------------------------
START TRANSACTION;
USE `runconf_db`;
INSERT INTO `runconf_db`.`run_configurations` (`id`, `run_number`, `trigger_configuration_id`, `daq_id`, `started`, `finished`) VALUES (1, 1000, 1, 1, NULL, NULL);

COMMIT;


-- -----------------------------------------------------
-- Data for table `runconf_db`.`readout_mask_presets`
-- -----------------------------------------------------
START TRANSACTION;
USE `runconf_db`;
INSERT INTO `runconf_db`.`readout_mask_presets` (`id`, `version`, `values`, `board_id`) VALUES (1, 0, '1.01 1.02 1.03 1.04 1.1 1.11 1.12 1.13 2.0 2.1 2.3 5.123 6.123 16.123 1.01', 1);
INSERT INTO `runconf_db`.`readout_mask_presets` (`id`, `version`, `values`, `board_id`) VALUES (2, 1, '1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 ', 1);
INSERT INTO `runconf_db`.`readout_mask_presets` (`id`, `version`, `values`, `board_id`) VALUES (3, 0, '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ', 2);

COMMIT;


-- -----------------------------------------------------
-- Data for table `runconf_db`.`board_configurations`
-- -----------------------------------------------------
START TRANSACTION;
USE `runconf_db`;
INSERT INTO `runconf_db`.`board_configurations` (`id`, `board_id`, `dac_preset_id`, `readout_mask_id`, `trigger_mask_id`, `readout_threshold_id`, `trigger_threshold_id`, `trigger_baseline_id`, `readout_baseline_id`, `board_parameter_id`) VALUES (1, 1, NULL, 1, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `runconf_db`.`board_configurations` (`id`, `board_id`, `dac_preset_id`, `readout_mask_id`, `trigger_mask_id`, `readout_threshold_id`, `trigger_threshold_id`, `trigger_baseline_id`, `readout_baseline_id`, `board_parameter_id`) VALUES (2, 2, NULL, 3, NULL, NULL, NULL, NULL, NULL, NULL);

COMMIT;


-- -----------------------------------------------------
-- Data for table `runconf_db`.`board_configurations_has_run_configurations`
-- -----------------------------------------------------
START TRANSACTION;
USE `runconf_db`;
INSERT INTO `runconf_db`.`board_configurations_has_run_configurations` (`board_configuration_id`, `run_configuration_id`) VALUES (1, 1);

COMMIT;


-- -----------------------------------------------------
-- Data for table `runconf_db`.`crates`
-- -----------------------------------------------------
START TRANSACTION;
USE `runconf_db`;
INSERT INTO `runconf_db`.`crates` (`id`, `name`, `created`) VALUES (1, 'test_rock', NULL);

COMMIT;

