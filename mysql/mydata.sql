-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.4.8-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             10.2.0.5599
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for device
CREATE DATABASE IF NOT EXISTS `device` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `device`;

-- Dumping structure for table device.devicedetail
CREATE TABLE IF NOT EXISTS `devicedetail` (
  `deviceid` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(15) NOT NULL,
  `community` varchar(20) NOT NULL,
  `active` tinyint(4) NOT NULL COMMENT '1 is on',
  `serialnumber` varchar(50) DEFAULT NULL,
  `brand` varchar(50) DEFAULT NULL,
  `contractnumber` varchar(50) DEFAULT NULL COMMENT 'เลขที่สัญญา',
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`deviceid`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table device.devicelocation
CREATE TABLE IF NOT EXISTS `devicelocation` (
  `locationID` int(11) NOT NULL AUTO_INCREMENT,
  `deviceid` int(11) DEFAULT NULL,
  `build` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `node` varchar(255) DEFAULT NULL,
  `rack` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`locationID`),
  KEY `deviceid` (`deviceid`),
  CONSTRAINT `devicelocation_ibfk_1` FOREIGN KEY (`deviceid`) REFERENCES `devicedetail` (`deviceid`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table device.icmpstatus
CREATE TABLE IF NOT EXISTS `icmpstatus` (
  `icmpid` int(11) NOT NULL AUTO_INCREMENT,
  `icmpstatus` varchar(20) NOT NULL COMMENT '1 is up 0 is down',
  `deviceid` int(11) DEFAULT NULL,
  `timedate` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`icmpid`),
  KEY `deviceid` (`deviceid`),
  CONSTRAINT `icmpstatus_ibfk_1` FOREIGN KEY (`deviceid`) REFERENCES `devicedetail` (`deviceid`)
) ENGINE=InnoDB AUTO_INCREMENT=23887 DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table device.portsnmpstatus
CREATE TABLE IF NOT EXISTS `portsnmpstatus` (
  `deviceid` int(11) DEFAULT NULL,
  `icmpid` int(11) DEFAULT NULL,
  `portIndex` varchar(20) DEFAULT NULL,
  `porttype` varchar(100) DEFAULT NULL,
  `portstatus` varchar(20) DEFAULT NULL,
  `portpotocol` varchar(20) DEFAULT NULL,
  KEY `deviceid` (`deviceid`),
  KEY `icmpid` (`icmpid`),
  CONSTRAINT `portsnmpstatus_ibfk_1` FOREIGN KEY (`deviceid`) REFERENCES `devicedetail` (`deviceid`),
  CONSTRAINT `portsnmpstatus_ibfk_2` FOREIGN KEY (`icmpid`) REFERENCES `icmpstatus` (`icmpid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table device.snmpstatus
CREATE TABLE IF NOT EXISTS `snmpstatus` (
  `deviceid` int(11) DEFAULT NULL,
  `icmpid` int(11) DEFAULT NULL,
  `hostname` varchar(100) DEFAULT NULL,
  `upTime` int(11) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  KEY `deviceid` (`deviceid`),
  KEY `icmpid` (`icmpid`),
  CONSTRAINT `snmpstatus_ibfk_1` FOREIGN KEY (`deviceid`) REFERENCES `devicedetail` (`deviceid`),
  CONSTRAINT `snmpstatus_ibfk_2` FOREIGN KEY (`icmpid`) REFERENCES `icmpstatus` (`icmpid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.

-- Dumping structure for table device.user
CREATE TABLE IF NOT EXISTS `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(1000) NOT NULL,
  `firstname` varchar(50) NOT NULL,
  `lastname` varchar(50) NOT NULL,
  `usertype` bit(1) NOT NULL COMMENT '1 is admin 0 is user',
  `email` varchar(255) DEFAULT NULL,
  `emailAlert` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`,`username`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8;


INSERT INTO `user` (`id`, `username`, `password`, `firstname`, `lastname`, `usertype`, `email`, `emailAlert`) VALUES
	(31, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', 'admin', b'1', 'admin@admin.com', 0);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
-- Data exporting was unselected.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
