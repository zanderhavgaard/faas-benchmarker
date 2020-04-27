
create database if not exists Benchmarks;
use Benchmarks;


SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE TABLE IF NOT EXISTS `Experiment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(100) DEFAULT NULL,
  `timing` BIGINT NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

INSERT INTO Experiment (uuid,timing) VALUES (1406,200);