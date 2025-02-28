-- MySQL dump 10.13  Distrib 9.2.0, for macos14.7 (x86_64)
--
-- Host: localhost    Database: blood_bank
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `BloodBank`
--

DROP TABLE IF EXISTS `BloodBank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BloodBank` (
  `id` int NOT NULL AUTO_INCREMENT,
  `blood_group` varchar(5) NOT NULL,
  `units_available` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BloodBank`
--

LOCK TABLES `BloodBank` WRITE;
/*!40000 ALTER TABLE `BloodBank` DISABLE KEYS */;
INSERT INTO `BloodBank` VALUES (1,'A+',0),(2,'A-',0),(3,'B+',0),(4,'B-',0),(5,'AB+',0),(6,'AB-',0),(7,'O+',0),(8,'O-',0);
/*!40000 ALTER TABLE `BloodBank` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DonationSchedule`
--

DROP TABLE IF EXISTS `DonationSchedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DonationSchedule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `donor_id` int DEFAULT NULL,
  `scheduled_date` date NOT NULL,
  `time_slot` varchar(20) NOT NULL,
  `status` enum('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
  `notes` text,
  PRIMARY KEY (`id`),
  KEY `donor_id` (`donor_id`),
  CONSTRAINT `donationschedule_ibfk_1` FOREIGN KEY (`donor_id`) REFERENCES `Donors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DonationSchedule`
--

LOCK TABLES `DonationSchedule` WRITE;
/*!40000 ALTER TABLE `DonationSchedule` DISABLE KEYS */;
INSERT INTO `DonationSchedule` VALUES (1,1,'2025-02-28','','Scheduled',''),(2,2,'2025-02-28','','Scheduled',''),(3,3,'2025-02-28','','Scheduled','');
/*!40000 ALTER TABLE `DonationSchedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Donors`
--

DROP TABLE IF EXISTS `Donors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Donors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `age` int NOT NULL,
  `blood_group` varchar(5) NOT NULL,
  `contact_info` varchar(100) NOT NULL,
  `donation_date` date NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` text,
  `health_status` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Donors`
--

LOCK TABLES `Donors` WRITE;
/*!40000 ALTER TABLE `Donors` DISABLE KEYS */;
INSERT INTO `Donors` VALUES (1,'Bernard Bosro',45,'A-','0593706706','2025-02-28','misterbosro@gmail.com','Ablekuma',''),(2,'Philipina Aidoo',34,'O+','1234567890','2025-02-28','phil@gmail.com','Lapaz',''),(3,'Divine Horsoo',37,'B+','1234567890','2025-02-28','divine@gmail.com','Achimota','');
/*!40000 ALTER TABLE `Donors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Inventory_Alerts`
--

DROP TABLE IF EXISTS `Inventory_Alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Inventory_Alerts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `blood_group` varchar(5) NOT NULL,
  `alert_type` enum('Low','Critical') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Inventory_Alerts`
--

LOCK TABLES `Inventory_Alerts` WRITE;
/*!40000 ALTER TABLE `Inventory_Alerts` DISABLE KEYS */;
/*!40000 ALTER TABLE `Inventory_Alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Requests`
--

DROP TABLE IF EXISTS `Requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hospital_name` varchar(100) NOT NULL,
  `blood_group` varchar(5) NOT NULL,
  `units_requested` int NOT NULL,
  `request_date` date NOT NULL,
  `status` enum('Pending','Approved','Rejected') DEFAULT 'Pending',
  `priority` enum('Normal','Urgent','Emergency') DEFAULT 'Normal',
  `notes` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Requests`
--

LOCK TABLES `Requests` WRITE;
/*!40000 ALTER TABLE `Requests` DISABLE KEYS */;
INSERT INTO `Requests` VALUES (1,'Ridge','AB+',20,'2025-02-28','Pending','Normal',''),(2,'Korle Bu','O-',10,'2025-02-28','Pending','Urgent','Please we need it urgently');
/*!40000 ALTER TABLE `Requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','staff') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
INSERT INTO `Users` VALUES (1,'admin','$2b$12$XlHAMsu9r.HEVcdV/XfRWOWMh7dvGr1zK9p7RNoSPPuZ9.8ZPNYbu','admin');
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-02-28 12:01:45
