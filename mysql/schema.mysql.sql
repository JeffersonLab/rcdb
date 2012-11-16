SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `triggerdb` ;
CREATE SCHEMA IF NOT EXISTS `triggerdb` DEFAULT CHARACTER SET latin1 ;
USE `triggerdb` ;

-- -----------------------------------------------------
-- Table `triggerdb`.`boards`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `triggerdb`.`boards` ;

CREATE  TABLE IF NOT EXISTS `triggerdb`.`boards` (
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
-- Table `triggerdb`.`pedestal_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `triggerdb`.`pedestal_presets` ;

CREATE  TABLE IF NOT EXISTS `triggerdb`.`pedestal_presets` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `values` VARCHAR(1045) NOT NULL ,
  `version` INT NOT NULL ,
  `board_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_pedestals_boards1_idx` (`board_id` ASC) ,
  CONSTRAINT `fk_pedestals_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `triggerdb`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerdb`.`baseline_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `triggerdb`.`baseline_presets` ;

CREATE  TABLE IF NOT EXISTS `triggerdb`.`baseline_presets` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `version` INT NOT NULL ,
  `values` VARCHAR(1024) NOT NULL ,
  `board_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_base_lines_boards1_idx` (`board_id` ASC) ,
  CONSTRAINT `fk_base_lines_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `triggerdb`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerdb`.`trigger_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `triggerdb`.`trigger_configurations` ;

CREATE  TABLE IF NOT EXISTS `triggerdb`.`trigger_configurations` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `type` VARCHAR(45) NOT NULL ,
  `parameters` INT NULL ,
  `prescale` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerdb`.`threshold_presets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `triggerdb`.`threshold_presets` ;

CREATE  TABLE IF NOT EXISTS `triggerdb`.`threshold_presets` (
  `id` INT NOT NULL ,
  `version` INT NOT NULL ,
  `values` VARCHAR(1024) NOT NULL ,
  `board_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_thresholds_boards1_idx` (`board_id` ASC) ,
  CONSTRAINT `fk_thresholds_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `triggerdb`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerdb`.`board_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `triggerdb`.`board_configurations` ;

CREATE  TABLE IF NOT EXISTS `triggerdb`.`board_configurations` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `board_id` INT NOT NULL ,
  `crait` INT NULL ,
  `slot` INT NULL ,
  `board_configurationscol` VARCHAR(45) NULL ,
  `board_configurationscol1` VARCHAR(45) NULL ,
  `threshold_presets_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_boards_configuration_boards1_idx` (`board_id` ASC) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  INDEX `fk_board_configurations_threshold_presets1_idx` (`threshold_presets_id` ASC) ,
  CONSTRAINT `fk_boards_configuration_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `triggerdb`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_board_configurations_threshold_presets1`
    FOREIGN KEY (`threshold_presets_id` )
    REFERENCES `triggerdb`.`threshold_presets` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerdb`.`run_configurations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `triggerdb`.`run_configurations` ;

CREATE  TABLE IF NOT EXISTS `triggerdb`.`run_configurations` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `run` INT NOT NULL DEFAULT 0 ,
  `trigger_configuration_id` INT NOT NULL ,
  `board_configuration_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_run_configuration_trigger_configuration1_idx` (`trigger_configuration_id` ASC) ,
  INDEX `fk_run_configuration_board_configurations1_idx` (`board_configuration_id` ASC) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  CONSTRAINT `fk_run_configuration_trigger_configuration1`
    FOREIGN KEY (`trigger_configuration_id` )
    REFERENCES `triggerdb`.`trigger_configurations` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_run_configuration_board_configurations1`
    FOREIGN KEY (`board_configuration_id` )
    REFERENCES `triggerdb`.`board_configurations` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `triggerdb`.`daq`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `triggerdb`.`daq` ;

CREATE  TABLE IF NOT EXISTS `triggerdb`.`daq` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `readout_mode` VARCHAR(45) NULL ,
  `window_size` INT NULL ,
  `nsa_nsb` VARCHAR(45) NULL ,
  `pulses_num` VARCHAR(45) NULL ,
  `block_readout` VARCHAR(45) NULL ,
  `loob_back` VARCHAR(45) NULL ,
  `chanel_mask` INT NULL ,
  `board_configuration_id` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `fk_daq_config_board_configurations1_idx` (`board_configuration_id` ASC) ,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) ,
  CONSTRAINT `fk_daq_config_board_configurations1`
    FOREIGN KEY (`board_configuration_id` )
    REFERENCES `triggerdb`.`board_configurations` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE = '';
GRANT USAGE ON *.* TO triggerdb;
 DROP USER triggerdb;
SET SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';
CREATE USER `triggerdb`;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `triggerdb`.`boards`
-- -----------------------------------------------------
START TRANSACTION;
USE `triggerdb`;
INSERT INTO `triggerdb`.`boards` (`id`, `board_type`, `name`, `serial`, `description`, `modified`, `firmware`) VALUES (1, 'FADC', 'test_one', '11', 'test board one', NULL, NULL);
INSERT INTO `triggerdb`.`boards` (`id`, `board_type`, `name`, `serial`, `description`, `modified`, `firmware`) VALUES (2, 'FADC', 'test_two', '12', 'test board two', NULL, NULL);

COMMIT;

-- -----------------------------------------------------
-- Data for table `triggerdb`.`pedestal_presets`
-- -----------------------------------------------------
START TRANSACTION;
USE `triggerdb`;
INSERT INTO `triggerdb`.`pedestal_presets` (`id`, `values`, `version`, `board_id`) VALUES (1, '10;20;30', 1, 1);

COMMIT;

-- -----------------------------------------------------
-- Data for table `triggerdb`.`baseline_presets`
-- -----------------------------------------------------
START TRANSACTION;
USE `triggerdb`;
INSERT INTO `triggerdb`.`baseline_presets` (`id`, `version`, `values`, `board_id`) VALUES (1, 1, '50;60;70', 1);

COMMIT;
