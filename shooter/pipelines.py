# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from scrapy.utils.project import get_project_settings
import logging

from shooter.items import MacroStatDataItem

settings = get_project_settings()


class ShooterPipeline:
    def process_item(self, item, spider):
        return item

class MysqlPipeline:
    def __init__(self):
        self.engines_ = {}
        self.sql_session_pools_ = {}
        self.engines_[settings.get("MYSQL_STOCK_DB_NAME")] = create_engine("mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (settings.get("MYSQL_USER"),
            settings.get("MYSQL_PASSWORD"), settings.get("MYSQL_HOST"), settings.get("MYSQL_PORT"),
            settings.get("MYSQL_STOCK_DB_NAME"), settings.get("MYSQL_CHARSET")), pool_size=5, pool_timeout=30)
        self.engines_[settings.get("MYSQL_MACRO_DB_NAME")] = create_engine("mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (settings.get("MYSQL_USER"),
            settings.get("MYSQL_PASSWORD"), settings.get("MYSQL_HOST"), settings.get("MYSQL_PORT"),
            settings.get("MYSQL_MACRO_DB_NAME"), settings.get("MYSQL_CHARSET")), pool_size=5, pool_timeout=30)
        for k,v in self.engines_.items():
            self.sql_session_pools_[k] = sessionmaker(bind=v)
        self.spider_name_ = None

    def open_spider(self, spider):
        self.spider_name_ = spider.name
        spider.log("------spider start: %s------" % (self.spider_name_), level=logging.INFO)

    def process_item(self, item, spider):
        spider.log("------spider:%s process item:%s------" % (self.spider_name_, type(item)), level=logging.INFO)
        # insert into db
        sql_update = " ON DUPLICATE KEY UPDATE "
        sql_fields = ""
        sql_values = ""
        for k,v in item.items():
            if k == "table_name_":
                continue
            if k == "db_name_":
                continue
            sql_fields += "%s," % (k)
            sql_values += "\"%s\"," % (v)
            sql_update += "%s=\"%s\"," % (k, v)
        sql_update = sql_update.strip(",")
        sql_fields = sql_fields.strip(",")
        sql_values = sql_values.strip(",")
        sql = "insert into %s (%s) values (%s)" % (item["table_name_"], sql_fields, sql_values) + sql_update
        spider.log(sql, level=logging.INFO)
        sql_session = scoped_session(self.sql_session_pools_[item["db_name_"]])
        sql_session.execute(sql)
        sql_session.commit()


    
