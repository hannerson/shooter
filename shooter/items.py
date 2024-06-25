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
    db_name_ = scrapy.Field()
    table_name_ = scrapy.Field()
    publish_date = scrapy.Field()
    content = scrapy.Field()
    publish_datetime = scrapy.Field()
    pass

class MacroStatDataItem(scrapy.Item):
    db_name_ = scrapy.Field()
    table_name_ = scrapy.Field()
    name = scrapy.Field()
    type = scrapy.Field()
    stype = scrapy.Field()
    stat_type = scrapy.Field()
    stat_date = scrapy.Field()
    value = scrapy.Field()
    pass

class StockCompanyItem(scrapy.Item):
    db_name_ = scrapy.Field()
    table_name_ = scrapy.Field()
    code = scrapy.Field()
    name = scrapy.Field()
    ename = scrapy.Field()
    region = scrapy.Field()
    oname = scrapy.Field()
    main_business = scrapy.Field()
    intro = scrapy.Field()
    address = scrapy.Field()
    chairman = scrapy.Field()
    CEO = scrapy.Field()
    registered_capital = scrapy.Field()
    no_employees = scrapy.Field()
    sw_industry_name = scrapy.Field()
    zjh_industry_code = scrapy.Field()
    zjh_industry_name = scrapy.Field()
    ths_industry_code = scrapy.Field()
    ths_industry_name = scrapy.Field()
    pass

class StockTradeInfoDayItem(scrapy.Item):
    db_name_ = scrapy.Field()
    table_name_ = scrapy.Field()
    code = scrapy.Field()
    name = scrapy.Field()
    tdate = scrapy.Field()
    oprice = scrapy.Field()
    cprice = scrapy.Field()
    hprice = scrapy.Field()
    lprice = scrapy.Field()
    intro = scrapy.Field()
    pb = scrapy.Field()
    pe = scrapy.Field()
    tvalue = scrapy.Field()
    cvalue = scrapy.Field()
    tamount = scrapy.Field()
    tprice = scrapy.Field()
    turnover = scrapy.Field()
    amplitude = scrapy.Field()
    change = scrapy.Field()
    change_rate = scrapy.Field()
    total_share = scrapy.Field()
    free_share = scrapy.Field()
    peg = scrapy.Field()
    pe_lyr = scrapy.Field()
    ps_ttm = scrapy.Field()
    pcf_ocf_ttm = scrapy.Field()
    pass

class CompanyCodeItem(scrapy.Item):
    db_name_ = scrapy.Field()
    table_name_ = scrapy.Field()
    code = scrapy.Field()
    zjh_industry_code = scrapy.Field()
    zjh_industry_name = scrapy.Field()
    ths_industry_code = scrapy.Field()
    ths_industry_name = scrapy.Field()
