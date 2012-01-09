SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

DROP SCHEMA IF EXISTS `confdb` ;
CREATE SCHEMA IF NOT EXISTS `confdb` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
USE `confdb` ;

-- -----------------------------------------------------
-- Table `confdb`.`boards`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `confdb`.`boards` ;

CREATE  TABLE IF NOT EXISTS `confdb`.`boards` (
  `id` INT NOT NULL ,
  `boardtype` VARCHAR(45) NOT NULL ,
  `name` VARCHAR(1024) NOT NULL ,
  `serial` VARCHAR(512) NOT NULL ,
  `description` VARCHAR(1024) NULL ,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `confdb`.`pedestals`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `confdb`.`pedestals` ;

CREATE  TABLE IF NOT EXISTS `confdb`.`pedestals` (
  `id` INT NOT NULL ,
  `values` VARCHAR(1045) NULL ,
  `version` INT NULL ,
  `board_id` INT NOT NULL ,
  PRIMARY KEY (`id`, `board_id`) ,
  INDEX `fk_pedestals_boards1` (`board_id` ASC) ,
  CONSTRAINT `fk_pedestals_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `confdb`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `confdb`.`base_lines`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `confdb`.`base_lines` ;

CREATE  TABLE IF NOT EXISTS `confdb`.`base_lines` (
  `id` INT NOT NULL ,
  `board_id` INT NOT NULL ,
  `values` VARCHAR(45) NULL ,
  `version` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`, `board_id`) ,
  INDEX `fk_base_lines_boards1` (`board_id` ASC) ,
  CONSTRAINT `fk_base_lines_boards1`
    FOREIGN KEY (`board_id` )
    REFERENCES `confdb`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `confdb`.`trigger_configuration`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `confdb`.`trigger_configuration` ;

CREATE  TABLE IF NOT EXISTS `confdb`.`trigger_configuration` (
  `id` INT NOT NULL ,
  `trigger_type` VARCHAR(45) NULL ,
  `loob_back` VARCHAR(45) NULL ,
  `window_size` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `confdb`.`boards_configuration`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `confdb`.`boards_configuration` ;

CREATE  TABLE IF NOT EXISTS `confdb`.`boards_configuration` (
  `id` INT NOT NULL ,
  `boards_id` INT NOT NULL ,
  `pedestals_id` INT NOT NULL ,
  `pedestals_board_id` INT NOT NULL ,
  `base_lines_id` INT NOT NULL ,
  `base_lines_board_id` INT NOT NULL ,
  PRIMARY KEY (`id`, `boards_id`, `pedestals_id`, `pedestals_board_id`, `base_lines_id`, `base_lines_board_id`) ,
  INDEX `fk_boards_configuration_boards1` (`boards_id` ASC) ,
  INDEX `fk_boards_configuration_pedestals1` (`pedestals_id` ASC, `pedestals_board_id` ASC) ,
  INDEX `fk_boards_configuration_base_lines1` (`base_lines_id` ASC, `base_lines_board_id` ASC) ,
  CONSTRAINT `fk_boards_configuration_boards1`
    FOREIGN KEY (`boards_id` )
    REFERENCES `confdb`.`boards` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_boards_configuration_pedestals1`
    FOREIGN KEY (`pedestals_id` )
    REFERENCES `confdb`.`pedestals` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_boards_configuration_base_lines1`
    FOREIGN KEY (`base_lines_id` , `base_lines_board_id` )
    REFERENCES `confdb`.`base_lines` (`id` , `board_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `confdb`.`run_configuration`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `confdb`.`run_configuration` ;

CREATE  TABLE IF NOT EXISTS `confdb`.`run_configuration` (
  `id` INT NOT NULL ,
  `trigger_configuration_id` INT NOT NULL ,
  `boards_configuration_id` INT NOT NULL ,
  `boards_configuration_boards_id` INT NOT NULL ,
  `boards_configuration_pedestals_id` INT NOT NULL ,
  `boards_configuration_pedestals_board_id` INT NOT NULL ,
  `boards_configuration_base_lines_id` INT NOT NULL ,
  `boards_configuration_base_lines_board_id` INT NOT NULL ,
  PRIMARY KEY (`id`, `trigger_configuration_id`, `boards_configuration_id`, `boards_configuration_boards_id`, `boards_configuration_pedestals_id`, `boards_configuration_pedestals_board_id`, `boards_configuration_base_lines_id`, `boards_configuration_base_lines_board_id`) ,
  INDEX `fk_run_configuration_trigger_configuration1` (`trigger_configuration_id` ASC) ,
  INDEX `fk_run_configuration_boards_configuration1` (`boards_configuration_id` ASC, `boards_configuration_boards_id` ASC, `boards_configuration_pedestals_id` ASC, `boards_configuration_pedestals_board_id` ASC, `boards_configuration_base_lines_id` ASC, `boards_configuration_base_lines_board_id` ASC) ,
  CONSTRAINT `fk_run_configuration_trigger_configuration1`
    FOREIGN KEY (`trigger_configuration_id` )
    REFERENCES `confdb`.`trigger_configuration` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_run_configuration_boards_configuration1`
    FOREIGN KEY (`boards_configuration_id` , `boards_configuration_boards_id` , `boards_configuration_pedestals_id` , `boards_configuration_pedestals_board_id` , `boards_configuration_base_lines_id` , `boards_configuration_base_lines_board_id` )
    REFERENCES `confdb`.`boards_configuration` (`id` , `boards_id` , `pedestals_id` , `pedestals_board_id` , `base_lines_id` , `base_lines_board_id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `confdb`.`triggers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `confdb`.`triggers` ;

CREATE  TABLE IF NOT EXISTS `confdb`.`triggers` (
  `id` INT NOT NULL ,
  `type` VARCHAR(45) NULL ,
  `prescaling` VARCHAR(45) NULL ,
  `trigger_configuration_id` INT NOT NULL ,
  PRIMARY KEY (`id`, `trigger_configuration_id`) ,
  INDEX `fk_triggers_trigger_configuration1` (`trigger_configuration_id` ASC) ,
  CONSTRAINT `fk_triggers_trigger_configuration1`
    FOREIGN KEY (`trigger_configuration_id` )
    REFERENCES `confdb`.`trigger_configuration` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `confdb`.`boards`
-- -----------------------------------------------------
START TRANSACTION;
USE `confdb`;
INSERT INTO `confdb`.`boards` (`id`, `boardtype`, `name`, `serial`, `description`, `modified`) VALUES (1, 'FADC', 'one', '11', 'test one', NULL);

COMMIT;

-- -----------------------------------------------------
-- Data for table `confdb`.`pedestals`
-- -----------------------------------------------------
START TRANSACTION;
USE `confdb`;
INSERT INTO `confdb`.`pedestals` (`id`, `values`, `version`, `board_id`) VALUES (1, '10;20;30', 1, 1);

COMMIT;

-- -----------------------------------------------------
-- Data for table `confdb`.`base_lines`
-- -----------------------------------------------------
START TRANSACTION;
USE `confdb`;
INSERT INTO `confdb`.`base_lines` (`id`, `board_id`, `values`, `version`) VALUES (1, 1, '50;60;70', '1');

COMMIT;
