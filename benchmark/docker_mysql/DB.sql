
create database Benchmarks;
use Benchmarks;


SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

-- Table of all experiments and its meta data
CREATE TABLE IF NOT EXISTS `Experiment` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `experiment_meta_identifier` varchar(100) NOT NULL,
  `uuid` varchar(36) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` varchar(200) NOT NULL,
  `cl_provider` varchar(100) NOT NULL,
  `cl_client` varchar(100) NOT NULL,
  `python_version` varchar(50) NOT NULL,
  `cores` INT NOT NULL,
  `memory` BIGINT NOT NULL,
  `start_time` DOUBLE NOT NULL,
  `end_time` DOUBLE NOT NULL,
  `total_time` DOUBLE NOT NULL,
  `dev_mode` BOOLEAN DEFAULT FALSE,
  UNIQUE(uuid),
  PRIMARY KEY (id)
) ENGINE=InnoDB;

-- Table of all invocations and their data, linked to an experiment
CREATE TABLE IF NOT EXISTS `Invocation` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exp_id` varchar(36) NOT NULL,
  `root_identifier`varchar(100) NOT NULL,
  `identifier` varchar(100) NOT NULL,
  `function_name` varchar(50) NOT NULL,
  `uuid` varchar(36),
  `parent` varchar(100) NOT NULL,
  `level` INT NOT NULL,
  `sleep` DOUBLE NOT NULL,
  `instance_identifier` varchar(100) NOT NULL,
  `python_version` varchar(50) NOT NULL,
  `function_cores` INT NOT NULL,
  `memory` BIGINT NOT NULL,
  `throughput` BIGINT DEFAULT 0.0 NOT NULL,
  `throughput_time` DOUBLE DEFAULT 0.0 NOT NULL,
  `throughput_process_time` DOUBLE DEFAULT 0.0 NOT NULL,
  `throughput_running_time` DOUBLE DEFAULT 0.0 NOT NULL,
  `random_seed` INT DEFAULT -1 NOT NULL,
  `cpu` varchar(100) DEFAULT 'unknown' NOT NULL,
  `process_time` DOUBLE DEFAULT 0.0 NOT NULL,
  `numb_threads` INT NOT NULL,
  `thread_id` INT NOT NULL,
  `execution_start` DOUBLE NOT NULL,
  `execution_end` DOUBLE NOT NULL,
  `invocation_start` DOUBLE NOT NULL,
  `invocation_end` DOUBLE NOT NULL,
  `execution_total` DOUBLE NOT NULL,
  `invocation_total` DOUBLE NOT NULL,
  UNIQUE(identifier),
  PRIMARY KEY (id),
  FOREIGN KEY (exp_id) REFERENCES Experiment(uuid) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- table to collect data regarding thrown exceptions
-- have to use bad practice with possible many NULL values due to unpredictability of exceptions
CREATE TABLE IF NOT EXISTS `Error` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exp_id`varchar(36) NOT NULL,
  `root_identifier` varchar(100) NOT NULL,
  `identifier` varchar(100) NOT NULL,
  `function_name`varchar(50) NOT NULL,
  `type` varchar(100) NOT NULL,
  `trace` varchar(1500) NOT NULL,
  `message` varchar(100) NOT NULL,
  `uuid` varchar(36) DEFAULT 'unknown' NOT NULL,
  `parent` varchar(100) DEFAULT 'unknown' NOT NULL,
  `sleep` DOUBLE DEFAULT 0.0 NOT NULL,
  `python_version` varchar(100) DEFAULT 'unknown' NOT NULL,
  `function_cores`INT DEFAULT 0 NOT NULL,
  `level` INT DEFAULT -1 NOT NULL,
  `memory` BIGINT DEFAULT 0 NOT NULL,
  `throughput` BIGINT DEFAULT 0 NOT NULL,
  `throughput_time` DOUBLE DEFAULT 0.0 NOT NULL,
  `throughput_process_time` DOUBLE DEFAULT 0.0 NOT NULL,
  `throughput_running_time` DOUBLE DEFAULT 0.0 NOT NULL,
  `random_seed` INT DEFAULT -1 NOT NULL,
  `cpu` varchar(100) DEFAULT 'unknown' NOT NULL,
  `process_time` DOUBLE DEFAULT 0.0 NOT NULL,
  `numb_threads` INT DEFAULT 0 NOT NULL,
  `thread_id` INT DEFAULT 0 NOT NULL,
  `instance_identifier` varchar(100) DEFAULT 'unknwn' NOT NULL,
  `execution_start` DOUBLE DEFAULT 0.0 NOT NULL,
  `execution_end` DOUBLE DEFAULT 0.0 NOT NULL,
  `invocation_start` DOUBLE DEFAULT 0.0 NOT NULL,
  `invocation_end` DOUBLE DEFAULT 0.0 NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (exp_id) REFERENCES Experiment(uuid) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS  `Monolith` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exp_id`varchar(36) NOT NULL,
  `invo_id` varchar(100) NOT NULL,
  `seed` INT DEFAULt 0,
  `function_argument` INT DEFAULT 0,
  `function_called` varchar(50) NOT NULL,
  `process_time_matrix` DOUBLE DEFAULT 0.0,
  `running_time_matrix` DOUBLE DEFAULT 0.0,
  PRIMARY KEY (id),
  FOREIGN KEY (exp_id) REFERENCES Experiment(uuid) ON DELETE CASCADE,
  FOREIGN KEY (invo_id) REFERENCES Invocation(identifier)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;


CREATE TABLE IF NOT EXISTS `Monolith` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exp_id`varchar(36) NOT NULL,
  `invo_id` varchar(100) NOT NULL,
  `seed` INT DEFAULt 0,
  `function_argument` INT DEFAULT 0,
  `function_called` varchar(50) NOT NULL,
  `process_time_matrix` DOUBLE DEFAULT 0.0,
  `running_time_matrix` DOUBLE DEFAULT 0.0,
  PRIMARY KEY (id),
  FOREIGN KEY (exp_id) REFERENCES Experiment(uuid) ON DELETE CASCADE,
  FOREIGN KEY (invo_id) REFERENCES Invocation(identifier)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `Coldstart` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exp_id`varchar(36) NOT NULL,
  `invo_id` varchar(100) NOT NULL,
  `minutes` INT DEFAULt 0 NOT NULL,
  `seconds` INT DEFAULT 0,
  `granularity` INT NOT NULL,
  `multithreaded` BOOLEAN DEFAULT FALSE,
  `cold` BOOLEAN DEFAULT TRUE,
  `final` BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (id),
  FOREIGN KEY (exp_id) REFERENCES Experiment(uuid) ON DELETE CASCADE,
  FOREIGN KEY (invo_id) REFERENCES Invocation(identifier)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS  `Function_lifetime` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exp_id`varchar(36) NOT NULL,
  `instance_identifier` varchar(100) NOT NULL,
  `hours` INT DEFAULT 0 NOT NULL,
  `minutes` INT DEFAULT 0 NOT NULL,
  `seconds` INT DEFAULT 0,
  `sleep_time` INT DEFAULT 0 NOT NULL,
  `reclaimed` BOOLEAN DEFAULT TRUE,
  PRIMARY KEY (id),
  FOREIGN KEY (exp_id) REFERENCES Experiment(uuid) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `Cc_bench` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exp_id`varchar(36) NOT NULL,
  `function_name` varchar(50) NOT NULL,
  `numb_threads` INT NOT NULL,
  `errors` INT NOT NULL,
  `throughput_time` DOUBLE NOT NULL,
  `acc_throughput` DOUBLE NOT NULL,
  `acc_process_time` DOUBLE NOT NULL,
  `cores` DOUBLE NOT NULL,
  `success_rate` DOUBLE NOT NULL,
  `acc_execution_start` DOUBLE NOT NULL,
  `acc_execution_end` DOUBLE NOT NULL,
  `acc_invocation_start` DOUBLE NOT NULL,
  `acc_invocation_end` DOUBLE NOT NULL,
  `acc_execution_total` DOUBLE NOT NULL,
  `acc_invocation_total` DOUBLE NOT NULL,
  `acc_latency` DOUBLE NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`exp_id`) REFERENCES Experiment(uuid) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS `Function_lifecycle` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `exp_id`varchar(36) NOT NULL,
  `function_name` varchar(50) NOT NULL,
  `numb_invokations` INT NOT NULL,
  `throughput_time` DOUBLE NOT NULL,
  `errors` INT NOT NULL,
  `unique_instances` INT NOT NULL,
  `distribution` DOUBLE NOT NULL,
  `error_dist` DOUBLE NOT NULL,
  `diff_from_orig` INT NOT NULL,
  `identifiers` varchar(700) NOT NULL,
  `repeats_from_orig` varchar(700) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`exp_id`) REFERENCES Experiment(uuid) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

