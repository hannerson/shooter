# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scrapy.utils.project import get_project_settings
import logging

settings = get_project_settings()


class ShooterPipeline:
    def process_item(self, item, spider):
        return item

class MacroDataPipeline:
    def __init__(self):
        self.engine_ = create_engine("mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (settings.get("MYSQL_USER"),
            settings.get("MYSQL_PASSWORD"), settings.get("MYSQL_HOST"), settings.get("MYSQL_PORT"),
            settings.get("MYSQL_MACRO_DB_NAME"), settings.get("MYSQL_CHARSET")), pool_size=5, pool_timeout=30)
        self.sql_session_pool_ = sessionmaker(bind=self.engine_)
        self.spider_name_ = None

    def open_spider(self, spider):
        self.spider_name_ = spider.name
        spider.log("------spider start------", level=logging.INFO)

    def process_item(self, item, spider):
        spider.log("------process item------", level=logging.INFO)

    
