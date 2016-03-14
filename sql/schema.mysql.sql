SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `rcdb` ;
CREATE SCHEMA IF NOT EXISTS `rcdb` DEFAULT CHARACTER SET latin1 ;
USE `rcdb` ;

-- -----------------------------------------------------
-- Table `rcdb`.`boards`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`boards` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`boards` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `board_type` VARCHAR(45) NOT NULL,
  `serial` VARCHAR(512) NOT NULL,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`runs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`runs` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`runs` (
  `number` INT UNSIGNED NOT NULL,
  `started` DATETIME NULL DEFAULT NULL,
  `finished` DATETIME NULL DEFAULT NULL,
  `total_events` INT NOT NULL DEFAULT 0,
  PRIMARY KEY (`number`),
  UNIQUE INDEX `run_number_UNIQUE` (`number` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`readout_mask_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`readout_mask_presets` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`readout_mask_presets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards1`
    FOREIGN KEY (`board_id`)
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`trigger_mask_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`trigger_mask_presets` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`trigger_mask_presets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards10`
    FOREIGN KEY (`board_id`)
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`readout_threshold_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`readout_threshold_presets` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`readout_threshold_presets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards11`
    FOREIGN KEY (`board_id`)
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`trigger_threshold_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`trigger_threshold_presets` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`trigger_threshold_presets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards110`
    FOREIGN KEY (`board_id`)
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`trigger_baseline_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`trigger_baseline_presets` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`trigger_baseline_presets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards1100`
    FOREIGN KEY (`board_id`)
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`readout_baseline_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`readout_baseline_presets` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`readout_baseline_presets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards101`
    FOREIGN KEY (`board_id`)
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`dac_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`dac_presets` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`dac_presets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards100`
    FOREIGN KEY (`board_id`)
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`board_parameter_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`board_parameter_presets` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`board_parameter_presets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `version` INT NOT NULL,
  `values` VARCHAR(1024) NOT NULL,
  `board_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC),
  CONSTRAINT `fk_thresholds_boards1010`
    FOREIGN KEY (`board_id`)
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`board_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`board_configurations` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`board_configurations` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `board_id` INT UNSIGNED NOT NULL,
  `dac_preset_id` INT UNSIGNED NULL,
  `readout_mask_id` INT UNSIGNED NULL,
  `trigger_mask_id` INT UNSIGNED NULL,
  `readout_threshold_id` INT UNSIGNED NULL,
  `trigger_threshold_id` INT UNSIGNED NULL,
  `trigger_baseline_id` INT UNSIGNED NULL,
  `readout_baseline_id` INT UNSIGNED NULL,
  `board_parameter_id` INT UNSIGNED NULL,
  `version` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  INDEX `fk_boards_configuration_boards1_idx` (`board_id` ASC),
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
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_threshold_presets1`
    FOREIGN KEY (`readout_mask_id`)
    REFERENCES `rcdb`.`readout_mask_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_trigger_masks1`
    FOREIGN KEY (`trigger_mask_id`)
    REFERENCES `rcdb`.`trigger_mask_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_readout_thresholds1`
    FOREIGN KEY (`readout_threshold_id`)
    REFERENCES `rcdb`.`readout_threshold_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_trigger_thresholds1`
    FOREIGN KEY (`trigger_threshold_id`)
    REFERENCES `rcdb`.`trigger_threshold_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_trigger_baselines1`
    FOREIGN KEY (`trigger_baseline_id`)
    REFERENCES `rcdb`.`trigger_baseline_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_readout_baselines1`
    FOREIGN KEY (`readout_baseline_id`)
    REFERENCES `rcdb`.`readout_baseline_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_dacs1`
    FOREIGN KEY (`dac_preset_id`)
    REFERENCES `rcdb`.`dac_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_board_parameters1`
    FOREIGN KEY (`board_parameter_id`)
    REFERENCES `rcdb`.`board_parameter_presets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`trigger_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`trigger_configurations` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`trigger_configurations` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(45) NOT NULL,
  `parameters` TEXT NULL,
  `prescale` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`run_parameters`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`run_parameters` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`run_parameters` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
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
-- Table `rcdb`.`board_configurations_have_runs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`board_configurations_have_runs` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`board_configurations_have_runs` (
  `board_configuration_id` INT UNSIGNED NOT NULL,
  `run_number` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`board_configuration_id`, `run_number`),
  INDEX `fk_board_configurations_has_run_configurations_board_config_idx` (`board_configuration_id` ASC),
  INDEX `fk_board_configurations_have_runs_runs1_idx` (`run_number` ASC),
  CONSTRAINT `fk_board_configurations_has_run_configurations_board_configur1`
    FOREIGN KEY (`board_configuration_id`)
    REFERENCES `rcdb`.`board_configurations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_have_runs_runs1`
    FOREIGN KEY (`run_number`)
    REFERENCES `rcdb`.`runs` (`number`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
PACK_KEYS = DEFAULT;


-- -----------------------------------------------------
-- Table `rcdb`.`files`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`files` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`files` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `path` TEXT NOT NULL,
  `sha256` VARCHAR(44) NOT NULL,
  `content` LONGTEXT NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
ENGINE = InnoDB
COMMENT = 'Table contains original coda and board configuration files';


-- -----------------------------------------------------
-- Table `rcdb`.`crates`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`crates` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`crates` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`board_installations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`board_installations` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`board_installations` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `slot` INT NOT NULL DEFAULT 0,
  `board_id` INT UNSIGNED NOT NULL,
  `crate_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_boards_configuration_boards1_idx` (`board_id` ASC),
  INDEX `fk_board_configurations_crates1_idx` (`crate_id` ASC),
  CONSTRAINT `fk_boards_configuration_boards10`
    FOREIGN KEY (`board_id`)
    REFERENCES `rcdb`.`boards` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_crates10`
    FOREIGN KEY (`crate_id`)
    REFERENCES `rcdb`.`crates` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`board_installations_have_runs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`board_installations_have_runs` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`board_installations_have_runs` (
  `board_installation_id` INT UNSIGNED NOT NULL,
  `run_number` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`board_installation_id`, `run_number`),
  INDEX `fk_table1_board_installations1_idx` (`board_installation_id` ASC),
  INDEX `fk_board_installations_have_runs_runs1_idx` (`run_number` ASC),
  CONSTRAINT `fk_table1_board_installations1`
    FOREIGN KEY (`board_installation_id`)
    REFERENCES `rcdb`.`board_installations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_installations_have_runs_runs1`
    FOREIGN KEY (`run_number`)
    REFERENCES `rcdb`.`runs` (`number`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`files_have_runs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`files_have_runs` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`files_have_runs` (
  `files_id` INT UNSIGNED NOT NULL,
  `run_number` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`files_id`, `run_number`),
  INDEX `fk_files_has_run_configuration_files1_idx` (`files_id` ASC),
  INDEX `fk_files_has_run_configurations_runs1_idx` (`run_number` ASC),
  CONSTRAINT `fk_files_has_run_configuration_files1`
    FOREIGN KEY (`files_id`)
    REFERENCES `rcdb`.`files` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_files_has_run_configurations_runs1`
    FOREIGN KEY (`run_number`)
    REFERENCES `rcdb`.`runs` (`number`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`condition_types`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`condition_types` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`condition_types` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `value_type` VARCHAR(32) NOT NULL DEFAULT 'text',
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_many_per_run` BIT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `key_UNIQUE` (`name` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`logs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`logs` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`logs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `table_ids` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `related_run` INT NULL DEFAULT NULL,
  `user_name` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rcdb`.`schema_version`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`schema_version` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`schema_version` (
  `version` INT NOT NULL,
  PRIMARY KEY (`version`),
  UNIQUE INDEX `version_UNIQUE` (`version` ASC))
ENGINE = InnoDB
COMMENT = 'Shows version of rcdb schema\n';


-- -----------------------------------------------------
-- Table `rcdb`.`conditions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rcdb`.`conditions` ;

CREATE TABLE IF NOT EXISTS `rcdb`.`conditions` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `run_number` INT UNSIGNED NOT NULL,
  `condition_type_id` INT UNSIGNED NOT NULL,
  `text_value` LONGTEXT NULL DEFAULT NULL,
  `int_value` INT NOT NULL DEFAULT 0,
  `float_value` FLOAT NOT NULL DEFAULT 0,
  `bool_value` BIT NOT NULL DEFAULT 0,
  `time` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`, `run_number`, `condition_type_id`),
  INDEX `fk_condition_values_runs1_idx` (`run_number` ASC),
  INDEX `fk_condition_values_conditions1_idx` (`condition_type_id` ASC),
  CONSTRAINT `fk_condition_values_runs1`
    FOREIGN KEY (`run_number`)
    REFERENCES `rcdb`.`runs` (`number`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_condition_values_conditions1`
    FOREIGN KEY (`condition_type_id`)
    REFERENCES `rcdb`.`condition_types` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
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
-- Data for table `rcdb`.`boards`
-- -----------------------------------------------------
START TRANSACTION;
USE `rcdb`;
INSERT INTO `rcdb`.`boards` (`id`, `board_type`, `serial`, `modified`) VALUES (1, 'FADC', '11', NULL);
INSERT INTO `rcdb`.`boards` (`id`, `board_type`, `serial`, `modified`) VALUES (2, 'FADC', '12', NULL);

COMMIT;


-- -----------------------------------------------------
-- Data for table `rcdb`.`readout_mask_presets`
-- -----------------------------------------------------
START TRANSACTION;
USE `rcdb`;
INSERT INTO `rcdb`.`readout_mask_presets` (`id`, `version`, `values`, `board_id`) VALUES (1, 0, '1.01 1.02 1.03 1.04 1.1 1.11 1.12 1.13 2.0 2.1 2.3 5.123 6.123 16.123 1.01', 1);
INSERT INTO `rcdb`.`readout_mask_presets` (`id`, `version`, `values`, `board_id`) VALUES (2, 1, '1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 ', 1);
INSERT INTO `rcdb`.`readout_mask_presets` (`id`, `version`, `values`, `board_id`) VALUES (3, 0, '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ', 2);

COMMIT;


-- -----------------------------------------------------
-- Data for table `rcdb`.`trigger_configurations`
-- -----------------------------------------------------
START TRANSACTION;
USE `rcdb`;
INSERT INTO `rcdb`.`trigger_configurations` (`id`, `type`, `parameters`, `prescale`) VALUES (1, 'unknown', '1', '1 2 3');
INSERT INTO `rcdb`.`trigger_configurations` (`id`, `type`, `parameters`, `prescale`) VALUES (2, 'test', '2', '1 2 3');

COMMIT;


-- -----------------------------------------------------
-- Data for table `rcdb`.`schema_version`
-- -----------------------------------------------------
START TRANSACTION;
USE `rcdb`;
INSERT INTO `rcdb`.`schema_version` (`version`) VALUES (2);

COMMIT;

