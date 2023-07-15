# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ShooterItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MacroPubNoticeItem(scrapy.Item):
    table_name = scrapy.Field()
    publish_date = scrapy.Field()
    content = scrapy.Field()
    publish_datetime = scrapy.Field()
    pass

class MacroStatDataItem(scrapy.Item):
    table_name = scrapy.Field()
    name = scrapy.Field()
    type = scrapy.Field()
    stype = scrapy.Field()
    stat_type = scrapy.Field()
    stat_date = scrapy.Field()
    value = scrapy.Field()
    pass
