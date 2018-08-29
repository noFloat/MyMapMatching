/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50712
 Source Host           : localhost
 Source Database       : mapmatching

 Target Server Type    : MySQL
 Target Server Version : 50712
 File Encoding         : utf-8

 Date: 08/29/2018 13:06:21 PM
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `beijing_node`
-- ----------------------------
DROP TABLE IF EXISTS `beijing_node`;
CREATE TABLE `beijing_node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lon` varchar(255) DEFAULT NULL,
  `lat` varchar(255) DEFAULT NULL,
  `gaode_lon` varchar(255) DEFAULT NULL,
  `gaode_lat` varchar(255) DEFAULT NULL,
  `node_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `beijing_node_graphhopper`
-- ----------------------------
DROP TABLE IF EXISTS `beijing_node_graphhopper`;
CREATE TABLE `beijing_node_graphhopper` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_id` int(11) DEFAULT NULL,
  `lat` text,
  `lon` text,
  `gaode_lat` text,
  `gaode_lon` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `beijing_route_graphhopper`
-- ----------------------------
DROP TABLE IF EXISTS `beijing_route_graphhopper`;
CREATE TABLE `beijing_route_graphhopper` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_node_id` int(11) DEFAULT NULL,
  `target_node_id` int(11) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `node_list` text,
  `way_list` text,
  `transfer_times` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `beijing_way`
-- ----------------------------
DROP TABLE IF EXISTS `beijing_way`;
CREATE TABLE `beijing_way` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` bigint(11) DEFAULT NULL,
  `target_id` bigint(11) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `foot` int(11) DEFAULT NULL,
  `car` int(11) DEFAULT NULL,
  `bike` int(11) DEFAULT NULL,
  `street_name` varchar(255) DEFAULT NULL,
  `highway` varchar(255) DEFAULT NULL,
  `way_id` bigint(11) DEFAULT NULL,
  `wkt` text,
  `graphhopper_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `beijing_way_graphhopper`
-- ----------------------------
DROP TABLE IF EXISTS `beijing_way_graphhopper`;
CREATE TABLE `beijing_way_graphhopper` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `edge_id` int(11) DEFAULT NULL,
  `from_node_id` int(11) DEFAULT NULL,
  `target_node_id` int(11) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `street_name_one` varchar(255) DEFAULT NULL,
  `street_name_two` varchar(255) DEFAULT NULL,
  `wkt` text,
  `wkt_gaode` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `chengdu_node_graphhopper`
-- ----------------------------
DROP TABLE IF EXISTS `chengdu_node_graphhopper`;
CREATE TABLE `chengdu_node_graphhopper` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_id` int(11) DEFAULT NULL,
  `lat` text,
  `lon` text,
  `gaode_lat` text,
  `gaode_lon` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `chengdu_route_graphhopper`
-- ----------------------------
DROP TABLE IF EXISTS `chengdu_route_graphhopper`;
CREATE TABLE `chengdu_route_graphhopper` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_node_id` int(11) DEFAULT NULL,
  `target_node_id` int(11) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `node_list` text,
  `way_list` text,
  `transfer_times` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `chengdu_way_graphhopper`
-- ----------------------------
DROP TABLE IF EXISTS `chengdu_way_graphhopper`;
CREATE TABLE `chengdu_way_graphhopper` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `edge_id` int(11) DEFAULT NULL,
  `from_node_id` int(11) DEFAULT NULL,
  `target_node_id` int(11) DEFAULT NULL,
  `length` double DEFAULT NULL,
  `street_name_one` varchar(255) DEFAULT NULL,
  `street_name_two` varchar(255) DEFAULT NULL,
  `wkt` text,
  `wkt_gaode` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `eggs`
-- ----------------------------
DROP TABLE IF EXISTS `eggs`;
CREATE TABLE `eggs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category` int(11) DEFAULT NULL,
  `description` text,
  `imgsrc1` text,
  `imgsrc2` text,
  `imgsrc3` text,
  `answer` text,
  `title` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `semantic`
-- ----------------------------
DROP TABLE IF EXISTS `semantic`;
CREATE TABLE `semantic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `arrive` text,
  `departure` text,
  `location` text,
  `label` varchar(255) DEFAULT NULL,
  `restaurant` int(11) DEFAULT NULL,
  `market` int(11) DEFAULT NULL,
  `life` int(11) DEFAULT NULL,
  `school` int(11) DEFAULT NULL,
  `industry` int(11) DEFAULT NULL,
  `company` int(11) DEFAULT NULL,
  `residence` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `semantic`
-- ----------------------------
BEGIN;
INSERT INTO `semantic` VALUES ('1', '1', '2017-03-14 00:25', '2017-03-14 00:05', '104.057581,30.67253', 'Home', '323', '574', '135', '13', '4', '168', '13');
COMMIT;

-- ----------------------------
--  Table structure for `trajectory`
-- ----------------------------
DROP TABLE IF EXISTS `trajectory`;
CREATE TABLE `trajectory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` varchar(255) DEFAULT NULL,
  `lon` varchar(255) DEFAULT NULL,
  `lat` varchar(255) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `gaode_lon` varchar(255) DEFAULT NULL,
  `gaode_lat` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;
