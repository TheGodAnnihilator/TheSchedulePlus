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
-- Table structure for table `project_manager`
--

DROP TABLE IF EXISTS `project_manager`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_manager` (
  `pm_id` int NOT NULL AUTO_INCREMENT,
  `client_id` varchar(255) NOT NULL,
  `manager_name` varchar(255) NOT NULL,
  `notes` longtext,
  PRIMARY KEY (`pm_id`),
  KEY `project_manager_ibfk_1` (`client_id`),
  CONSTRAINT `project_manager_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`client_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_manager`
--

LOCK TABLES `project_manager` WRITE;
/*!40000 ALTER TABLE `project_manager` DISABLE KEYS */;
INSERT INTO `project_manager` VALUES (1,'AC','Kathleen Farren',NULL),(2,'AMA','Sara Berg',NULL),(3,'AR','Yvonne M. Bullard',NULL),(4,'AR','Nathan A. St John',NULL),(6,'AR','Morgan Mansfield',NULL),(7,'AR','Eric Dolph',NULL),(8,'AR','James Maurer',NULL),(10,'AR','Joseph Arndt',NULL),(11,'AR','John Conaty',NULL),(12,'AR','Rylie P. Podger',NULL),(13,'BY','Mark Lojek',NULL),(15,'BY','Jon Chu',NULL),(16,'CLI','Sean Payton',NULL),(17,'CRC','Sri Gundappa',NULL),(18,'CRC','Rohit Patel',NULL),(19,'CRC','Jignesh Barad',NULL),(20,'IC','Ankit Gajjar',NULL),(21,'IC','Igor Barshak',NULL),(22,'IC','Kerolos Salib',NULL),(23,'IC','Jevon Johnson',NULL),(24,'IC','Virginia Pugliese',NULL),(25,'OC','Marco Desa',NULL),(26,'OC','Jimmy Maldonado',NULL),(27,'PET','Aladin Accilien',NULL),(28,'S5P','Raymond Brown',NULL),(29,'S5P','Melissa Bergen',NULL),(30,'DEL','Steve Smith',NULL),(31,'TDP','Tej Patel',NULL),(32,'DG','Marvin Rodriguez',NULL),(33,'AR','Peter Murad',NULL),(34,'IC','Adam Edwards',NULL),(35,'AR','Carl Richardson',NULL),(36,'IC','Iqbalpreet Singh',NULL);
/*!40000 ALTER TABLE `project_manager` ENABLE KEYS */;
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
