CREATE DATABASE  IF NOT EXISTS `atomick` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `atomick`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: atomick
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Table structure for table `financial_params`
--

DROP TABLE IF EXISTS `financial_params`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `financial_params` (
  `param_id` int NOT NULL,
  `market_discount` decimal(5,2) DEFAULT NULL,
  `iva_rate` decimal(5,2) DEFAULT NULL,
  `commission_rate` decimal(5,2) DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`param_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `financial_params`
--

LOCK TABLES `financial_params` WRITE;
/*!40000 ALTER TABLE `financial_params` DISABLE KEYS */;
INSERT INTO `financial_params` VALUES (1,0.80,0.21,0.27,'2025-04-06 14:48:56');
/*!40000 ALTER TABLE `financial_params` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `insumos`
--

DROP TABLE IF EXISTS `insumos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `insumos` (
  `ID_Insumo` varchar(10) NOT NULL,
  `Nombre_Insumo` varchar(100) NOT NULL,
  `Unidad_Medida_Compra` varchar(20) DEFAULT NULL,
  `Costo_Compra` decimal(10,2) DEFAULT NULL,
  `Unidad_Medida_Uso` varchar(10) DEFAULT NULL,
  `Costo_Por_Unidad_Uso` decimal(12,5) DEFAULT NULL,
  `Categoria_TipoSupply` varchar(50) DEFAULT NULL,
  `Categoria_TipoMateria` varchar(50) DEFAULT NULL,
  `Fecha_Ultima_Actualizacion_Costo` date DEFAULT NULL,
  PRIMARY KEY (`ID_Insumo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `insumos`
--

LOCK TABLES `insumos` WRITE;
/*!40000 ALTER TABLE `insumos` DISABLE KEYS */;
INSERT INTO `insumos` VALUES ('IN001','Harina 000','Bolsa 25kg',5000.00,'g',0.20000,'No Perecedero','Seco','2025-04-01'),('IN002','Agua Corriente','Metro Cubico',50.00,'ml',0.00005,'Servicio','Liquido','2025-03-15'),('IN003','Sal Fina','Paquete 1kg',200.00,'g',0.20000,'No Perecedero','Condimento','2025-04-01'),('IN004','Levadura Fresca','Paquete 50g',150.00,'g',3.00000,'Perecedero','Otro','2025-04-03'),('IN005','Tomate Perita Pelado','Lata 800g',400.00,'g',0.50000,'No Perecedero','Vegetal','2025-04-02'),('IN006','Aceite Oliva Virgen Extra','Botella 1L',2000.00,'ml',2.00000,'No Perecedero','Grasa','2025-04-01'),('IN007','Queso Mozzarella','Horma 4kg',8000.00,'g',2.00000,'Perecedero','Lacteo','2025-04-03'),('IN008','Albahaca Fresca','Atado 50g',100.00,'g',2.00000,'Perecedero','Vegetal','2025-04-04'),('IN009','Caja Pizza Carton','unidad',5500.00,'unidad',NULL,'Packaging','Carton','2025-04-06'),('IN010','Separador Plastico Pizza','Paquete 100u',1000.00,'unidad',10.00000,'Packaging','Plastico','2025-03-20');
/*!40000 ALTER TABLE `insumos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `platos`
--

DROP TABLE IF EXISTS `platos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `platos` (
  `ID_Plato` varchar(10) NOT NULL,
  `Nombre_Plato` varchar(100) NOT NULL,
  `ID_Receta` varchar(10) DEFAULT NULL,
  `Costo_Receta_Base` decimal(12,5) DEFAULT NULL,
  `Costo_Total_Packaging` decimal(12,5) DEFAULT NULL,
  `Costo_Total_Plato` decimal(12,5) DEFAULT NULL,
  `Precio_Competencia` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID_Plato`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `platos`
--

LOCK TABLES `platos` WRITE;
/*!40000 ALTER TABLE `platos` DISABLE KEYS */;
INSERT INTO `platos` VALUES ('PL001','Pizza Margarita para Llevar','R001',563.40500,60.00000,623.40500,1200.00);
/*!40000 ALTER TABLE `platos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `platos_financials_history`
--

DROP TABLE IF EXISTS `platos_financials_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `platos_financials_history` (
  `SnapshotID` int NOT NULL AUTO_INCREMENT,
  `SnapshotTimestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ID_Plato` varchar(10) NOT NULL,
  `Costo_Plato_Hist` decimal(12,5) DEFAULT NULL,
  `Precio_Competencia_Hist` decimal(10,2) DEFAULT NULL,
  `Market_Discount_Used` decimal(5,2) DEFAULT NULL,
  `IVA_Rate_Used` decimal(5,2) DEFAULT NULL,
  `Commission_Rate_Used` decimal(5,2) DEFAULT NULL,
  `PBA_Hist` decimal(10,2) DEFAULT NULL,
  `PNA_Hist` decimal(10,2) DEFAULT NULL,
  `COGS_Partner_Actual_Hist` decimal(10,5) DEFAULT NULL,
  `Costo_Total_CT_Hist` decimal(12,5) DEFAULT NULL,
  `Margen_Bruto_Actual_MBA_Hist` decimal(10,2) DEFAULT NULL,
  `Porcentaje_Margen_Bruto_PctMBA_Hist` decimal(10,5) DEFAULT NULL,
  PRIMARY KEY (`SnapshotID`),
  KEY `idx_history_plato_time` (`ID_Plato`,`SnapshotTimestamp`),
  KEY `idx_history_time` (`SnapshotTimestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `platos_financials_history`
--

LOCK TABLES `platos_financials_history` WRITE;
/*!40000 ALTER TABLE `platos_financials_history` DISABLE KEYS */;
INSERT INTO `platos_financials_history` VALUES (1,'2025-04-06 16:51:14','PL001',573.30500,1000.00,0.80,0.21,0.27,800.00,661.16,0.86712,789.30500,-128.15,-0.19382),(2,'2025-04-06 16:56:59','PL001',573.30500,1200.00,0.80,0.21,0.27,960.00,793.39,0.72260,832.50500,-39.12,-0.04930);
/*!40000 ALTER TABLE `platos_financials_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `platos_packaging`
--

DROP TABLE IF EXISTS `platos_packaging`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `platos_packaging` (
  `ID_Composicion_P` int NOT NULL AUTO_INCREMENT,
  `ID_Plato` varchar(10) DEFAULT NULL,
  `ID_Insumo_Packaging` varchar(10) DEFAULT NULL,
  `Cantidad_Packaging` int DEFAULT NULL,
  `Costo_Item_Packaging` decimal(12,5) DEFAULT NULL,
  PRIMARY KEY (`ID_Composicion_P`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `platos_packaging`
--

LOCK TABLES `platos_packaging` WRITE;
/*!40000 ALTER TABLE `platos_packaging` DISABLE KEYS */;
INSERT INTO `platos_packaging` VALUES (1,'PL001','IN009',1,50.00000),(2,'PL001','IN010',1,10.00000);
/*!40000 ALTER TABLE `platos_packaging` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetas_composicion`
--

DROP TABLE IF EXISTS `recetas_composicion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas_composicion` (
  `ID_Composicion_R` int NOT NULL AUTO_INCREMENT,
  `ID_Receta` varchar(10) DEFAULT NULL,
  `ID_Componente` varchar(10) DEFAULT NULL,
  `Tipo_Componente` varchar(10) DEFAULT NULL,
  `Cantidad_Componente` decimal(10,3) DEFAULT NULL,
  `Unidad_Medida_Componente` varchar(20) DEFAULT NULL,
  `Costo_Componente_En_Receta` decimal(12,5) DEFAULT NULL,
  PRIMARY KEY (`ID_Composicion_R`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas_composicion`
--

LOCK TABLES `recetas_composicion` WRITE;
/*!40000 ALTER TABLE `recetas_composicion` DISABLE KEYS */;
INSERT INTO `recetas_composicion` VALUES (1,'R001','SR001','Subreceta',1.000,'unidad',63.10500),(2,'R001','SR002','Subreceta',0.150,'kg',90.30000),(3,'R001','IN007','Insumo',200.000,'g',400.00000),(4,'R001','IN008','Insumo',5.000,'g',10.00000);
/*!40000 ALTER TABLE `recetas_composicion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetas_definicion`
--

DROP TABLE IF EXISTS `recetas_definicion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas_definicion` (
  `ID_Receta` varchar(10) NOT NULL,
  `Nombre_Receta` varchar(100) NOT NULL,
  `Unidad_Medida_Receta` varchar(20) DEFAULT NULL,
  `Rendimiento_Receta` decimal(10,3) DEFAULT NULL,
  `Costo_Total_Receta` decimal(12,5) DEFAULT NULL,
  `Costo_Unitario_Receta` decimal(12,5) DEFAULT NULL,
  PRIMARY KEY (`ID_Receta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas_definicion`
--

LOCK TABLES `recetas_definicion` WRITE;
/*!40000 ALTER TABLE `recetas_definicion` DISABLE KEYS */;
INSERT INTO `recetas_definicion` VALUES ('R001','Pizza Margarita Base','unidad',1.000,563.40500,563.40500);
/*!40000 ALTER TABLE `recetas_definicion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subrecetas_composicion`
--

DROP TABLE IF EXISTS `subrecetas_composicion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subrecetas_composicion` (
  `ID_Composicion_SR` int NOT NULL AUTO_INCREMENT,
  `ID_Subreceta` varchar(10) DEFAULT NULL,
  `ID_Insumo` varchar(10) DEFAULT NULL,
  `Cantidad_Insumo` decimal(10,3) DEFAULT NULL,
  `Unidad_Medida_Insumo` varchar(10) DEFAULT NULL,
  `Costo_Insumo_En_Subreceta` decimal(12,5) DEFAULT NULL,
  PRIMARY KEY (`ID_Composicion_SR`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subrecetas_composicion`
--

LOCK TABLES `subrecetas_composicion` WRITE;
/*!40000 ALTER TABLE `subrecetas_composicion` DISABLE KEYS */;
INSERT INTO `subrecetas_composicion` VALUES (1,'SR001','IN001',180.000,'g',36.00000),(2,'SR001','IN002',100.000,'ml',0.00500),(3,'SR001','IN003',5.000,'g',1.00000),(4,'SR001','IN004',2.000,'g',6.00000),(5,'SR001','IN006',10.000,'ml',20.00000),(6,'SR002','IN005',1000.000,'g',500.00000),(7,'SR002','IN006',50.000,'ml',100.00000),(8,'SR002','IN003',10.000,'g',2.00000);
/*!40000 ALTER TABLE `subrecetas_composicion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subrecetas_definicion`
--

DROP TABLE IF EXISTS `subrecetas_definicion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subrecetas_definicion` (
  `ID_Subreceta` varchar(10) NOT NULL,
  `Nombre_Subreceta` varchar(100) NOT NULL,
  `Unidad_Medida_Produccion` varchar(20) DEFAULT NULL,
  `Rendimiento_Produccion` decimal(10,3) DEFAULT NULL,
  `Costo_Total_Subreceta` decimal(12,5) DEFAULT NULL,
  `Costo_Unitario_Subreceta` decimal(12,5) DEFAULT NULL,
  PRIMARY KEY (`ID_Subreceta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subrecetas_definicion`
--

LOCK TABLES `subrecetas_definicion` WRITE;
/*!40000 ALTER TABLE `subrecetas_definicion` DISABLE KEYS */;
INSERT INTO `subrecetas_definicion` VALUES ('SR001','Masa Pizza Bollo 300g','unidad',1.000,63.10500,63.10500),('SR002','Salsa Tomate Casera','kg',1.000,602.00000,602.00000);
/*!40000 ALTER TABLE `subrecetas_definicion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_platos_costos`
--

DROP TABLE IF EXISTS `v_platos_costos`;
/*!50001 DROP VIEW IF EXISTS `v_platos_costos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_platos_costos` AS SELECT 
 1 AS `ID_Plato`,
 1 AS `Nombre_Plato`,
 1 AS `ID_Receta`,
 1 AS `Nombre_Receta`,
 1 AS `Costo_Receta_Base`,
 1 AS `Costo_Packaging_Total`,
 1 AS `Costo_Total_Plato_Calculado`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_platos_financials`
--

DROP TABLE IF EXISTS `v_platos_financials`;
/*!50001 DROP VIEW IF EXISTS `v_platos_financials`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_platos_financials` AS SELECT 
 1 AS `ID_Plato`,
 1 AS `Nombre_Plato`,
 1 AS `Costo_Plato`,
 1 AS `Precio_Competencia`,
 1 AS `PBA`,
 1 AS `PNA`,
 1 AS `COGS_Partner_Actual`,
 1 AS `Comision_Plataforma`,
 1 AS `Costo_Total_CT`,
 1 AS `Margen_Bruto_Actual_MBA`,
 1 AS `Porcentaje_Margen_Bruto_PctMBA`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_recetas_costos`
--

DROP TABLE IF EXISTS `v_recetas_costos`;
/*!50001 DROP VIEW IF EXISTS `v_recetas_costos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_recetas_costos` AS SELECT 
 1 AS `ID_Receta`,
 1 AS `Nombre_Receta`,
 1 AS `Unidad_Medida_Receta`,
 1 AS `Rendimiento_Receta`,
 1 AS `Costo_Total_Calculado`,
 1 AS `Costo_Unitario_Calculado`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_subrecetas_costos`
--

DROP TABLE IF EXISTS `v_subrecetas_costos`;
/*!50001 DROP VIEW IF EXISTS `v_subrecetas_costos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_subrecetas_costos` AS SELECT 
 1 AS `ID_Subreceta`,
 1 AS `Nombre_Subreceta`,
 1 AS `Unidad_Medida_Produccion`,
 1 AS `Rendimiento_Produccion`,
 1 AS `Costo_Total_Calculado`,
 1 AS `Costo_Unitario_Calculado`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `v_platos_costos`
--

/*!50001 DROP VIEW IF EXISTS `v_platos_costos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_platos_costos` AS with `packagingcosts` as (select `pp`.`ID_Plato` AS `ID_Plato`,sum((`pp`.`Cantidad_Packaging` * `i`.`Costo_Por_Unidad_Uso`)) AS `Total_Packaging_Cost` from (`platos_packaging` `pp` join `insumos` `i` on((`pp`.`ID_Insumo_Packaging` = `i`.`ID_Insumo`))) group by `pp`.`ID_Plato`) select `p`.`ID_Plato` AS `ID_Plato`,`p`.`Nombre_Plato` AS `Nombre_Plato`,`p`.`ID_Receta` AS `ID_Receta`,`vrc`.`Nombre_Receta` AS `Nombre_Receta`,`vrc`.`Costo_Unitario_Calculado` AS `Costo_Receta_Base`,coalesce(`pc`.`Total_Packaging_Cost`,0) AS `Costo_Packaging_Total`,(`vrc`.`Costo_Unitario_Calculado` + coalesce(`pc`.`Total_Packaging_Cost`,0)) AS `Costo_Total_Plato_Calculado` from ((`platos` `p` join `v_recetas_costos` `vrc` on((`p`.`ID_Receta` = `vrc`.`ID_Receta`))) left join `packagingcosts` `pc` on((`p`.`ID_Plato` = `pc`.`ID_Plato`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_platos_financials`
--

/*!50001 DROP VIEW IF EXISTS `v_platos_financials`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_platos_financials` AS with `currentparams` as (select `financial_params`.`market_discount` AS `market_discount`,`financial_params`.`iva_rate` AS `iva_rate`,`financial_params`.`commission_rate` AS `commission_rate` from `financial_params` where (`financial_params`.`param_id` = 1)), `platoprecioscalculados` as (select `vpc`.`ID_Plato` AS `ID_Plato`,`vpc`.`Nombre_Plato` AS `Nombre_Plato`,`vpc`.`Costo_Total_Plato_Calculado` AS `Costo_Total_Plato_Calculado`,`p`.`Precio_Competencia` AS `Precio_Competencia`,`cp`.`market_discount` AS `market_discount`,`cp`.`iva_rate` AS `iva_rate`,`cp`.`commission_rate` AS `commission_rate`,(`cp`.`market_discount` * `p`.`Precio_Competencia`) AS `PBA`,((`cp`.`market_discount` * `p`.`Precio_Competencia`) / (1 + `cp`.`iva_rate`)) AS `PNA` from ((`v_platos_costos` `vpc` join `platos` `p` on((`vpc`.`ID_Plato` = `p`.`ID_Plato`))) join `currentparams` `cp`) where ((`p`.`Precio_Competencia` is not null) and (`p`.`Precio_Competencia` > 0))) select `ppc`.`ID_Plato` AS `ID_Plato`,`ppc`.`Nombre_Plato` AS `Nombre_Plato`,`ppc`.`Costo_Total_Plato_Calculado` AS `Costo_Plato`,`ppc`.`Precio_Competencia` AS `Precio_Competencia`,`ppc`.`PBA` AS `PBA`,`ppc`.`PNA` AS `PNA`,(`ppc`.`Costo_Total_Plato_Calculado` / nullif(`ppc`.`PNA`,0)) AS `COGS_Partner_Actual`,`ppc`.`commission_rate` AS `Comision_Plataforma`,(`ppc`.`Costo_Total_Plato_Calculado` + (`ppc`.`PBA` * `ppc`.`commission_rate`)) AS `Costo_Total_CT`,(`ppc`.`PNA` - (`ppc`.`Costo_Total_Plato_Calculado` + (`ppc`.`PBA` * `ppc`.`commission_rate`))) AS `Margen_Bruto_Actual_MBA`,(1 - ((`ppc`.`Costo_Total_Plato_Calculado` + (`ppc`.`PBA` * `ppc`.`commission_rate`)) / nullif(`ppc`.`PNA`,0))) AS `Porcentaje_Margen_Bruto_PctMBA` from `platoprecioscalculados` `ppc` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_recetas_costos`
--

/*!50001 DROP VIEW IF EXISTS `v_recetas_costos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_recetas_costos` AS select `rd`.`ID_Receta` AS `ID_Receta`,`rd`.`Nombre_Receta` AS `Nombre_Receta`,`rd`.`Unidad_Medida_Receta` AS `Unidad_Medida_Receta`,`rd`.`Rendimiento_Receta` AS `Rendimiento_Receta`,sum((`rc`.`Cantidad_Componente` * (case `rc`.`Tipo_Componente` when 'Subreceta' then `vsc`.`Costo_Unitario_Calculado` when 'Insumo' then `i`.`Costo_Por_Unidad_Uso` else 0 end))) AS `Costo_Total_Calculado`,(case when ((`rd`.`Rendimiento_Receta` is null) or (`rd`.`Rendimiento_Receta` = 0)) then NULL else (sum((`rc`.`Cantidad_Componente` * (case `rc`.`Tipo_Componente` when 'Subreceta' then `vsc`.`Costo_Unitario_Calculado` when 'Insumo' then `i`.`Costo_Por_Unidad_Uso` else 0 end))) / `rd`.`Rendimiento_Receta`) end) AS `Costo_Unitario_Calculado` from (((`recetas_definicion` `rd` join `recetas_composicion` `rc` on((`rd`.`ID_Receta` = `rc`.`ID_Receta`))) left join `v_subrecetas_costos` `vsc` on(((`rc`.`ID_Componente` = `vsc`.`ID_Subreceta`) and (`rc`.`Tipo_Componente` = 'Subreceta')))) left join `insumos` `i` on(((`rc`.`ID_Componente` = `i`.`ID_Insumo`) and (`rc`.`Tipo_Componente` = 'Insumo')))) group by `rd`.`ID_Receta`,`rd`.`Nombre_Receta`,`rd`.`Unidad_Medida_Receta`,`rd`.`Rendimiento_Receta` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_subrecetas_costos`
--

/*!50001 DROP VIEW IF EXISTS `v_subrecetas_costos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_subrecetas_costos` AS select `sd`.`ID_Subreceta` AS `ID_Subreceta`,`sd`.`Nombre_Subreceta` AS `Nombre_Subreceta`,`sd`.`Unidad_Medida_Produccion` AS `Unidad_Medida_Produccion`,`sd`.`Rendimiento_Produccion` AS `Rendimiento_Produccion`,sum((`sc`.`Cantidad_Insumo` * `i`.`Costo_Por_Unidad_Uso`)) AS `Costo_Total_Calculado`,(case when ((`sd`.`Rendimiento_Produccion` is null) or (`sd`.`Rendimiento_Produccion` = 0)) then NULL else (sum((`sc`.`Cantidad_Insumo` * `i`.`Costo_Por_Unidad_Uso`)) / `sd`.`Rendimiento_Produccion`) end) AS `Costo_Unitario_Calculado` from ((`subrecetas_definicion` `sd` join `subrecetas_composicion` `sc` on((`sd`.`ID_Subreceta` = `sc`.`ID_Subreceta`))) join `insumos` `i` on((`sc`.`ID_Insumo` = `i`.`ID_Insumo`))) group by `sd`.`ID_Subreceta`,`sd`.`Nombre_Subreceta`,`sd`.`Unidad_Medida_Produccion`,`sd`.`Rendimiento_Produccion` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-06 15:00:25
