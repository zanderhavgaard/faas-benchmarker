
create database if not exists Benchmarks;
use Benchmarks;


SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

-- Table of all experiments and its meta data
CREATE TABLE IF NOT EXISTS `Experiment` (
  `e_uuid` varchar(36) NOT NULL,
  `e_name` varchar(100) NOT NULL,
  `e_desc` varchar(200) NOT NULL,
  `e_cl_providor` varchar(100) NOT NULL,
  `e_client` varchar(100) NOT NULL,
  `e_py_version` varchar(50) NOT NULL,
  `e_cores` INT NOT NULL,
  `e_memory` INT NOT NULL,
  `e_start_time` FLOAT NOT NULL,
  `e_end_time` FLOAT NOT NULL,
  `e_total_time` FLOAT NOT NULL,
  PRIMARY KEY (`e_uuid`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

-- Table of all invocations and their data, linked to an experiment
CREATE TABLE IF NOT EXISTS `Invocation` (
  `exp_id`varchar(36) NOT NULL,
  `root_identifier`varchar(100) NOT NULL,
  `identifier` varchar(100) NOT NULL,
  `function_name` varchar(50) NOT NULL,
  `uuid` varchar(36) NOT NULL,
  `parent` varchar(100) NOT NULL,
  `level` INT NOT NULL,
  `sleep` FLOAT NOT NULL,
  `instance_identifier` varchar(100) NOT NULL,
  `python_version` varchar(50) NOT NULL,
  `memory` INT NOT NULL,
  `throughput` FLOAT DEFAULT 0.0,
  `numb_threads` INT NOT NULL,
  `thread_id` INT NOT NULL,
  `execution_start` FLOAT NOT NULL,
  `execution_end` FLOAT NOT NULL,
  `invocation_start` FLOAT NOT NULL,
  `invocation_end` FLOAT NOT NULL,
  `execution_total` FLOAT NOT NULL,
  `invocation_total` FLOAT NOT NULL,
  PRIMARY KEY (`identifier`),
  FOREIGN KEY (`exp_id`) REFERENCES Experiment(e_uuid)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

-- table to collect data regarding thrown exceptions
-- have to use bad practice with possible many NULL values due to unpredictability of exceptions
CREATE TABLE IF NOT EXISTS `Error` (
  `exp_id`varchar(36) NOT NULL,
  `root_identifier` varchar(100) NOT NULL,
  `identifier` varchar(100) NOT NULL,
  `function_name`varchar(50) NOT NULL,
  `type` varchar(100) NOT NULL,
  `trace` varchar(1500) NOT NULL,
  `message` varchar(100) NOT NULL,
  `uuid` varchar(36) DEFAULT NULL ,
  `parent` varchar(100) DEFAULT NULL,
  `sleep` FLOAT DEFAULT 0.0,
  `python_version` varchar(100) DEFAULT NULL,
  `level` INT DEFAULT 0,
  `memory` INT DEFAULT 0,
  `numb_threads` INT NOT NULL,
  `thread_id` INT NOT NULL,
  `instance_identifier` varchar(100) DEFAULT NULL,
  `execution_start` FLOAT DEFAULT 0.0,
  `execution_end` FLOAT DEFAULT 0.0,
  `invocation_start` FLOAT DEFAULT 0.0,
  `invocation_end` FLOAT DEFAULT 0.0,
  PRIMARY KEY (identifier,execution_start,invocation_start),
  FOREIGN KEY (exp_id) REFERENCES Experiment(e_uuid)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `Coldstart` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exp_id`varchar(36) NOT NULL,
  `invo_id` varchar(100) NOT NULL,
  `minutes` INT NOT NULL,
  `seconds` INT DEFAULT 0,
  `cold` BOOLEAN DEFAULT TRUE,
  `final` BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (id),
  FOREIGN KEY (exp_id) REFERENCES Experiment(e_uuid),
  FOREIGN KEY (invo_id) REFERENCES Invocation(identifier)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

