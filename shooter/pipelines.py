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
        self.engine_ = create_engine("mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (settings.get("MYSQL_USER"),
            settings.get("MYSQL_PASSWORD"), settings.get("MYSQL_HOST"), settings.get("MYSQL_PORT"),
            settings.get("MYSQL_MACRO_DB_NAME"), settings.get("MYSQL_CHARSET")), pool_size=5, pool_timeout=30)
        self.sql_session_pool_ = sessionmaker(bind=self.engine_)
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
            if k == "table_name":
                continue
            sql_fields += "%s," % (k)
            sql_values += "\"%s\"," % (v)
            sql_update += "%s=\"%s\"," % (k, v)
        sql_update = sql_update.strip(",")
        sql_fields = sql_fields.strip(",")
        sql_values = sql_values.strip(",")
        sql = "insert into %s (%s) values (%s)" % (item["table_name"], sql_fields, sql_values) + sql_update
        spider.log(sql, level=logging.INFO)
        sql_session = scoped_session(self.sql_session_pool_)
        sql_session.execute(sql)
        sql_session.commit()


    
