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

create database if not exists `stock_data`;

use `stock_data`;

create table if not exists `company_code` (
    `id` BIGINT unsigned AUTO_INCREMENT,
    `code` varchar(64) NOT NULL DEFAULT '000000' comment '股票编码',
    `name` varchar(64) NOT NULL DEFAULT '' comment '股票名称',
    `zjh_industry_code` varchar(64) NOT NULL DEFAULT '0' comment '证监会行业分类',
    `zjh_industry_name` varchar(128) NOT NULL DEFAULT '' comment '证监会行业分类',
    `ths_industry_code` varchar(64) NOT NULL DEFAULT '0' comment '同花顺行业分类',
    `ths_industry_name` varchar(128) NOT NULL DEFAULT '' comment '同花顺行业分类',
    PRIMARY KEY (`id`),
    INDEX `zjh_code` (`zjh_industry_code`),
    INDEX `ths_code` (`ths_industry_code`),
    UNIQUE KEY `code` (`code`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

create table if not exists `company` (
    `id` BIGINT unsigned AUTO_INCREMENT,
    `code` varchar(64) NOT NULL DEFAULT '000000' comment '股票编码',
    `name` varchar(256) NOT NULL DEFAULT '' comment '公司名称',
    `ename` varchar(256) NOT NULL DEFAULT '' comment '公司英文名称',
    `region` varchar(128) NOT NULL DEFAULT '' comment '所属地域',
    `oname` varchar(256) NOT NULL DEFAULT '' comment '曾用名',
    `main_business` text comment '主营业务',
    `intro` text comment '公司介绍',
    `address` varchar(256) NOT NULL DEFAULT '' comment '公司地址',
    `chairman` varchar(64) NOT NULL DEFAULT '' comment '董事长',
    `CEO` varchar(64) NOT NULL DEFAULT '' comment '总经理',
    `registered_capital` double NOT NULL DEFAULT '0.0' comment '注册资本,单位万元',
    `no_employees` int NOT NULL DEFAULT '0' comment '员工人数',
    `sw_industry_name` varchar(128) NOT NULL DEFAULT '' comment '申万行业分类',
    `zjh_industry_code` varchar(64) NOT NULL DEFAULT '0' comment '证监会行业分类',
    `zjh_industry_name` varchar(128) NOT NULL DEFAULT '' comment '证监会行业分类',
    `ths_industry_code` varchar(64) NOT NULL DEFAULT '0' comment '同花顺行业分类',
    `ths_industry_name` varchar(128) NOT NULL DEFAULT '' comment '同花顺行业分类',
    PRIMARY KEY (`id`),
    INDEX `name` (`name`),
    INDEX `zjh_code` (`zjh_industry_code`),
    INDEX `ths_code` (`ths_industry_code`),
    UNIQUE KEY `code` (`code`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

create table if not exists `stock_trade_info_day`(
    `id` BIGINT unsigned AUTO_INCREMENT,
    `code` varchar(64) NOT NULL DEFAULT '000000' comment '股票编码',
    `name` varchar(64) NOT NULL DEFAULT '' comment '股票名称',
    `tdate` date NOT NULL comment '行情日期',
    `oprice` double NOT NULL DEFAULT '0.0' comment '开盘价',
    `cprice` double NOT NULL DEFAULT '0.0' comment '收盘价',
    `hprice` double NOT NULL DEFAULT '0.0' comment '最高价',
    `lprice` double NOT NULL DEFAULT '0.0' comment '最低价',
    `pb` double NOT NULL DEFAULT '0.0' comment '市净率',
    `pe` double NOT NULL DEFAULT '0.0' comment '动态市盈率',
    `tvalue` double NOT NULL DEFAULT '0.0' comment '总市值,单位亿',
    `cvalue` double NOT NULL DEFAULT '0.0' comment '流通市值,单位亿',
    `tamount` double NOT NULL DEFAULT '0.0' comment '成交量',
    `tprice` double NOT NULL DEFAULT '0.0' comment '成交额',
    `turnover` double NOT NULL DEFAULT '0.0' comment '换手率%',
    `amplitude` double NOT NULL DEFAULT '0.0' comment '振幅%',
    `change` double NOT NULL DEFAULT '0.0' comment '涨跌额',
    `change_rate` double NOT NULL DEFAULT '0.0' comment '涨跌幅%',
    `total_share` double NOT NULL DEFAULT '0.0' comment '总股本',
    `free_share` double NOT NULL DEFAULT '0.0' comment '流通股本',
    `peg` double NOT NULL DEFAULT '0.0' comment 'peg估值',
    `pe_lyr` double NOT NULL DEFAULT '0.0' comment '静态市盈率, last year ratio',
    `ps_ttm` double NOT NULL DEFAULT '0.0' comment '市销率',
    `pcf_ocf_ttm` double NOT NULL DEFAULT '0.0' comment '市现率',
    PRIMARY KEY (`id`),
    INDEX `code` (`code`),
    UNIQUE KEY `tdate_code` (`tdate`, `code`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

