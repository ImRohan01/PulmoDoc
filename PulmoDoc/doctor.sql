USE `pulmodoc`;
CREATE TABLE IF NOT EXISTS `patient_register` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
  	`fullname` varchar(100) NOT NULL,
    `email` varchar(100) NOT NULL,
  	`password` varchar(255) NOT NULL,
    `phone` int(10) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
