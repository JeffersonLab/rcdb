-- MySQL Workbench Synchronization
-- Generated: 2023-09-14 11:46
-- Model: New Model
-- Version: 1.0
-- Project: Name of the project
-- Author: romanov

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

CREATE TABLE IF NOT EXISTS `rcdb`.`aliases` (
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

DROP TABLE IF EXISTS `rcdb`.`trigger_thresholds` ;

DROP TABLE IF EXISTS `rcdb`.`trigger_masks` ;

DROP TABLE IF EXISTS `rcdb`.`readout_thresholds` ;

DROP TABLE IF EXISTS `rcdb`.`readout_masks` ;

DROP TABLE IF EXISTS `rcdb`.`dac_presets` ;

DROP TABLE IF EXISTS `rcdb`.`crates` ;

DROP TABLE IF EXISTS `rcdb`.`boards` ;

DROP TABLE IF EXISTS `rcdb`.`board_installations_have_runs` ;

DROP TABLE IF EXISTS `rcdb`.`board_installations` ;

DROP TABLE IF EXISTS `rcdb`.`board_configurations_have_runs` ;

DROP TABLE IF EXISTS `rcdb`.`board_configurations` ;

DROP TABLE IF EXISTS `rcdb`.`alembic_version` ;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
