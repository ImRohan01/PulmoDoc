CREATE DATABASE IF NOT EXISTS `pulmodoc`;
USE `pulmodoc`;
CREATE TABLE IF NOT EXISTS `patient_register` (
	`id` int NOT NULL AUTO_INCREMENT,
  	`fullname` varchar(100) NOT NULL,
    `email` varchar(100) NOT NULL,
  	`password` varchar(255) NOT NULL,
    `phone` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS `doctor_register` (
	`id` int NOT NULL AUTO_INCREMENT,
  	`fullname` varchar(100) NOT NULL,
    `email` varchar(100) NOT NULL,
  	`password` varchar(255) NOT NULL,
    `degree` varchar(100),
    `image` varchar(100),
    `phone` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `admin_register` (
	`id` int NOT NULL AUTO_INCREMENT,
  	`fullname` varchar(100) NOT NULL,
    `email` varchar(100) NOT NULL,
  	`password` varchar(255) NOT NULL,
    `phone` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `test_results` (
	`id` int NOT NULL AUTO_INCREMENT,
  	`utn` varchar(100) NOT NULL UNIQUE,
    `image` varchar(255) NOT NULL,
  	`result` varchar(100) NOT NULL,
    `docid` int NOT NULL,
    `patid` int NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`docid`) REFERENCES doctor_register(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`patid`) REFERENCES patient_register(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `feedback` (
	`id` int NOT NULL AUTO_INCREMENT,
  	`utn` varchar(100) NOT NULL,
    `text` varchar(255) NOT NULL,
    `docid` int,
    `patid` int,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`docid`) REFERENCES doctor_register(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`patid`) REFERENCES patient_register(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (`utn`) REFERENCES test_results(utn)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `diagnosis` (
	`id` int NOT NULL AUTO_INCREMENT,
  	`utn` varchar(100) NOT NULL,
    `diagnosis` varchar(255) NOT NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`utn`) REFERENCES test_results(utn)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
