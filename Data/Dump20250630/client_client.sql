CREATE DATABASE  IF NOT EXISTS `client` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `client`;
-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: client
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `client`
--

DROP TABLE IF EXISTS `client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `client` (
  `client_id` varchar(3) NOT NULL,
  `client_name` varchar(255) NOT NULL,
  `client_address` varchar(255) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `client`
--

LOCK TABLES `client` WRITE;
/*!40000 ALTER TABLE `client` DISABLE KEYS */;
INSERT INTO `client` VALUES ('AC','Accu-Cost Construction Consultants, Inc.','2 Park Avenue, 20th Floor,','New York','New York City','10016',NULL),('AMA','Ashley McGraw Architects, D.P.C.','125 East Jefferson Street, 15th Floor,','New York','Syracuse','13202',NULL),('AR','Architectural Resources','505 Franklin Street','New York','Buffalo','14202',NULL),('BY','Boyce Technologies, Inc.','47-22 Pearson Place,','New York','Syracuse','11109',NULL),('CLI','Consigli & Associates, LLC.','333 7th Avenue','New York','New York City','10001',NULL),('CRC','CRC Associates Inc','300 Maple Avenue','New Jersey','Newark','07080',NULL),('DEL','SUNY Delhi','PO Box 6000','New York','Rochester','13902',NULL),('DG','DiGERONIMO ARCHITECTS','650 From Road – Mack II, Suite 560,','New Jersey','Paterson','07652',NULL),('HE','Hershy Engineering & Consulting PC','267 Jewett Ave','New York','New York City','10301',NULL),('IC','Infinity Contracting Services, Corp.','112-20 14th Ave','New York','Yonkers','11356',NULL),('OC','Oliveira Contracting, Inc.','15 Albertson Ave.','New York','Buffalo','11507',NULL),('PET','PETK, Inc.','300 Hempstead Tpke. – Ste. 202','New York','Syracuse','11552',NULL),('S5P','Studio 5 Partnership','16-00 Route 208 South, Suite 305','New Jersey','Elizabeth','07410',NULL),('TDP','TDP Associates Inc.','153 Shepherd Lane','New York','New York City','11577',NULL);
/*!40000 ALTER TABLE `client` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-30 21:53:37
