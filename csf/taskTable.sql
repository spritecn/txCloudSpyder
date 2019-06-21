CREATE TABLE `task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `clientid` smallint(6) DEFAULT 1,
  `taskinfo` text DEFAULT NULL,
  `createtime` bigint(20) DEFAULT 0,
  `runtime` double(8,2) DEFAULT 0.00,
  `taskcount` smallint(6) DEFAULT NULL,
  `errorcount` smallint(6) DEFAULT 0,
  `errorinfo` text DEFAULT NULL,
  `finished` tinyint(4) NOT NULL DEFAULT 0,
  `result` text DEFAULT NULL,
  `useage` varchar(255) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1002 DEFAULT CHARSET=utf8;


CREATE TABLE `taskresult` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fid` int(11) DEFAULT NULL,
  `taskid` smallint(255) DEFAULT 0,
  `result` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `1` (`fid`),
  CONSTRAINT `1` FOREIGN KEY (`fid`) REFERENCES `task` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

