create database if not exists `macro_data`;

use `macro_data`;

create table if not exists `macro_stat_type` (
    `id` BIGINT unsigned AUTO_INCREMENT,
    `name` varchar(128) NOT NULL,
    `code` varchar(128) NOT NULL DEFAULT '',
    `desc` TEXT,
    PRIMARY KEY (`id`),
    UNIQUE KEY (`name`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

create table if not exists `macro_stat_data` (
    `id` BIGINT unsigned AUTO_INCREMENT,
    `name` varchar(128) NOT NULL comment '数据名称',
    `type` int NOT NULL comment '数据类型: 1-CPI, 2-PPI, 3-PMI, 4-M0, 5-M1, 6-M2',
    `stype` int NOT NULL comment '子类统计: 1-全部, 2-...',
    `stat_type` int not null comment '统计周期: 1-年度, 2-季度, 3-月度, 4-上年同月, 5-上年同期, 6-上月, 7-期末值',
    `stat_date` date not null comment '统计日期:年-月',
    `value` double not null DEFAULT '0.0' comment '统计数据值',
    PRIMARY KEY (`id`),
    UNIQUE KEY `stat_type_idx` (`type`,`stype`,`stat_type`,`stat_date`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

create table if not exists `macro_publish_notice` (
    `id` BIGINT unsigned AUTO_INCREMENT,
    `publish_date` date NOT NULL comment '发布日期',
    `publish_datetime` datetime NOT NULL comment '发布时刻',
    `content` varchar(512) NOT NULL DEFAULT '' comment '发布内容',
    PRIMARY KEY (`id`),
    INDEX `pdate` (`publish_date`),
    UNIQUE KEY `idx_dcontent` (`publish_date`, `content`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

