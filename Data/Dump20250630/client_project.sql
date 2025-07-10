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
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project` (
  `project_id` int NOT NULL AUTO_INCREMENT,
  `client_id` varchar(255) NOT NULL,
  `project_no` varchar(20) NOT NULL,
  `project_name` varchar(255) NOT NULL,
  `client_project_manager` varchar(255) DEFAULT NULL,
  `project_type` varchar(20) DEFAULT NULL,
  `project_status` varchar(20) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`project_id`),
  UNIQUE KEY `project_no` (`project_no`),
  KEY `project_ibfk_1` (`client_id`),
  CONSTRAINT `project_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`client_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
INSERT INTO `project` VALUES (72,'AC','PA-FA','LINCOLN TUNNEL - FIRE ALARM SYSTEM EVALUATION - NEW JERSEY ADMINISTRATIVE BUILDING','Kathleen Farren','Estimatic','In Progress',NULL),(73,'AC','TES','NJSDA - Trenton High Elementary Scheeol','Kathleen Farren','Estimatic','In Progress',NULL),(74,'AC','PIL','PILGRAM PSYCHIATRIC CENTER - REHAB. CONTROL ROOM AND OFFICE BUILDING 82','Kathleen Farren','Estimatic','In Progress',NULL),(75,'AMA','UB-COM','UB- Computer Center to Science Labs','Sara Berg','Estimatic','In Progress',NULL),(76,'AMA','GFR','24057 - Geneva Food Research Lab','Sara Berg','Estimatic','In Progress',NULL),(77,'BY','A-37628','A-37628 SANDY RESILIENCY:EEBCS AND MASS CALL SYSTEM UPGRADE','Jon Chu','Scheduling','In Progress',NULL),(78,'BY','C-52174','C-52174 Design Build Services for Passenger Identification CCTV at Various Locations','Mark Lojek','Scheduling','In Progress',NULL),(79,'CLI','SBU-CW','211096 Stony Brook Hospital Curtain Wall Façade Renovation Project','Sean Payton','Scheduling','In Progress',NULL),(80,'CRC','C-40853','C-40853 Design Build Services - CAMS Upgrade and Fire Alarm System & Sprinklers at Various Locations','Jignesh Barad','Scheduling','In Progress',NULL),(81,'CRC','C-43057','C-43057 - UPS Replacement and HVAC Installation','Rohit Patel','Scheduling','In Progress',NULL),(82,'CRC','C-52146','C-52146 Design Build Services-LIDS Installation for URT','Sri Gundappa','Scheduling','In Progress',NULL),(83,'CRC','D-37467','PBX UPGRADE AT 7 LOCATIONS','Rohit Patel','Scheduling','In Progress',NULL),(84,'OC','D264899','D264899 - Pavement Preservation (Concrete)','Marco Desa','Scheduling','In Progress',NULL),(85,'OC','HBCR21B','COMPONENT REHABILITATION OF 8 BRIDGES IN THE BOROUGHS OF THE BRONX, BROOKLYN AND QUEENS','Jimmy Maldonado','Scheduling','In Progress',NULL),(86,'OC','HWPR20MXC','NYCDDC - NON-STANDARD PEDESTRAIN RAMPS UPGRADES','Marco Desa','Scheduling','In Progress',NULL),(87,'PET','LT-234.226','INSTALLATION AND REPLACEMENT OF OVERHEIGHT STRUCTURES AND DETECTORS AT NY ENTRANCE, PHASE II','Aladin Accilien','Scheduling','In Progress',NULL),(88,'S5P','LGA-Doors','LGA-1001 WO #3  Bay Door #3 at Building 137','Melissa Bergen','Scheduling','In Progress',NULL),(89,'DEL','DEL-WELL','SUNY Delhi - Drill New Well at Lower Valley Campus','Steve Smith','Estimatic','In Progress',NULL),(90,'TDP','E-42265','E-42265 Rehabilitation of Yard Lighting and yard Fencing at Fresh Pond Yard','Tej Patel','Scheduling','In Progress',NULL),(91,'TDP','MH','D017583 - Emergency Generator / Low Voltage, Fire Alarm, System/Fire Protection System','Tej Patel','Scheduling','In Progress',NULL),(92,'TDP','QCB','Queens College - Central Boiler Plant Upgrade','Tej Patel','Scheduling','In Progress',NULL),(93,'TDP','COSI','College of Staten Island - Renovation to First Floor and Cellar with Associated Asbestos Removal','Tej Patel','Scheduling','In Progress',NULL),(94,'AR','BNCC-S','Buffalo Conventional Center - Soffit Repair','Joseph Arndt','Estimatic','In Progress',NULL),(95,'AR','Bonner','UB - Renovate Bonner Hall Labs','James Maurer','Estimatic','In Progress',NULL),(96,'AR','Bray-Hall','SUNY ESF - Bray Hall','Peter Murad','Estimatic','In Progress',NULL),(97,'AR','Canopy','Woodlawn Beach State Park - Solar Canopy','Morgan Mansfield','Estimatic','In Progress',NULL),(98,'AR','Pots-CC','SUNY Potsdam Crane Complex','Nathan A. St John','Estimatic','In Progress',NULL),(99,'AR','Dewit-EL','SUNY Ulster Dewit Library - Elevator Modernization','John Conaty','Estimatic','In Progress',NULL),(100,'AR','E&L-EL','SUNY New Paltz Esopus & Lenape - Elevator Modernization','John Conaty','Estimatic','In Progress',NULL),(101,'AR','Glen-Iris','Glen IRIS INN - Letchworth State Park','Morgan Mansfield','Estimatic','In Progress',NULL),(102,'AR','Helio','Broome Developmental Center - Helio Health Phase II Building 1 & 1G','Carl Richardson','Estimatic','In Progress',NULL),(103,'AR','UB-NSC','UB - Renovate Natural Science Complex Labs','James Maurer','Estimatic','In Progress',NULL),(104,'AR','Mhall','SUNY Fredonia Mason Hall','Yvonne M. Bullard','Estimatic','In Progress',NULL),(105,'AR','Morris','SUNY MORRISVILLE - BUTCHER LIBRARY','Yvonne M. Bullard','Estimatic','In Progress',NULL),(106,'AR','Morris-S','MORRISVILLE LIBRARY SURGE','Eric Dolph','Estimatic','In Progress',NULL),(107,'AR','NKI-EL','Nathan kline institute - Elevator Modernization','John Conaty','Estimatic','In Progress',NULL),(108,'AR','RPC-EL','ROCHESTER PSYCHIATRIC CENTER: BUILDINGS - Rehab Elevator','Rylie P. Podger','Estimatic','In Progress',NULL),(109,'AR','SP','Sam\'s Point Visitor Center - Wood Main Roof Framing Condition Assessment','Yvonne M. Bullard','Estimatic','In Progress',NULL),(110,'IC','C-33945','C-33945 - Component Repairs 207th Street Overhaul and Maintenance Facilities','Ankit Gajjar','Scheduling','In Progress',NULL),(111,'IC','C-34874','C-34874 Elec and Mech Systems Improvements at 130 Livingston Street','Adam Edwards','Scheduling','In Progress',NULL),(112,'IC','HS445R','Port Richmond High School, Staten Island - D020509 – COVID Vent, COVID Climate Control','Kerolos Salib','Scheduling','In Progress',NULL),(113,'IC','HC','Hunter College - Brookdale Building Decanting to Hunter College North West Building','Virginia Pugliese','Scheduling','In Progress',NULL),(114,'IC','HVR-210','HVR-210 Hillview Reservoir Chemical Addition Facili','Iqbalpreet Singh','Scheduling','In Progress',NULL),(115,'IC','IS072','IS072 - D019139 – Certificate of Occupancy / Chiller Replacement','Jevon Johnson','Scheduling','In Progress',NULL),(116,'IC','LIRR-FS','LIRR Contract # 6482 - FIRE WATER MAIN REPLACEMENT','Igor Barshak','Scheduling','In Progress',NULL),(117,'IC','WTC-964','World Trade Center – Contract WTC-964.004A - HVAC Upgrade for 3 WTC Elevation 386’-00”','Igor Barshak','Scheduling','In Progress',NULL);
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
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
