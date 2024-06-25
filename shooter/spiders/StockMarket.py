import scrapy
# from playwright.async_api import async_playwright
from scrapy.utils.project import get_project_settings
import time
import datetime
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
import json

from shooter.items import CompanyCodeItem, StockCompanyItem, StockTradeInfoDayItem

script_hy_list_page = """
function main(splash, args)
    splash.images_enabled = false
    assert(splash:go(args.url))
    assert(splash:wait(5))
    js = string.format("var pages = document.querySelectorAll('#m-page > a'); var cur_page_dom = pages[0]; for (var i=0;i<pages.length;i++){if (pages[i].getAttribute('page') == %d) {cur_page_dom=pages[i]; break;}} cur_page_dom.click();", args.page)
    splash:runjs(js)
    assert(splash:wait(5))
    return splash:html()
end
"""

class StockmarketSpider(scrapy.Spider):
    name = "StockMarket"
    allowed_domains = ["10jqka.com.cn"]
    start_urls = ["http://q.10jqka.com.cn/"]
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        # "Host": "q.10jqka.com.cn",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        # "Referer": "http://stockpage.10jqka.com.cn/",
    }
    cookies = {
        "__utma": "156575163.339254459.1689865504.1689865504.1689865504.1",
        "__utmz": "156575163.1689865504.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
        "spversion": "20130314",
        "Hm_lvt_722143063e4892925903024537075d0d": "1689865492,1691314733",
        "Hm_lvt_929f8b362150b1f77b477230541dbbc2": "1689865492,1691314736",
        "Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1": "1689865492,1691314736",
        "searchGuide": "sg",
        "historystock":"603132%7C*%7C837592%7C*%7C603799",
        #"v": "AzUEO-1XvSTYsNmY2NmfAEiXRLrqsunEs2bNGLda8az7jlskfwL5lEO23eRE"
        "v": "Aw4_DrLK5qtEIFKPOSxUXd-iX-_Vj9KJ5FOGbThXepHMm6BRoB8imbTj1nwL"
    }
    settings = get_project_settings()
    db_engine = create_engine("mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (settings.get("MYSQL_USER"),
            settings.get("MYSQL_PASSWORD"), settings.get("MYSQL_HOST"), settings.get("MYSQL_PORT"),
            settings.get("MYSQL_STOCK_DB_NAME"), settings.get("MYSQL_CHARSET")), pool_size=5, pool_timeout=30)
    sql_session = sessionmaker(bind=db_engine)
    # parameter
    hy_type = "zjh"
    # company/trade
    crawl_type = "company"

    def start_requests(self):
        print ("----------------------------------")
        print ("scrapy hy_type:", self.hy_type)
        print ("scrapy crawl_type:", self.crawl_type)
        print ("-----------------------------------")
        if self.hy_type == "zjh":
            url = "http://q.10jqka.com.cn/zjhhy/"
        elif self.hy_type == "ths":
            url = "http://q.10jqka.com.cn/thshy/"
        else:
            print("[ERROR] not support hy_type:", self.hy_type, ". must [zjh|ths]")
            return
        if self.crawl_type not in ["company","trade","company_code","trade_history"]:
            print("[ERROR] not support crawl_type:", self.crawl_type, "must [company|trade|company_code|trade_history]")
            return
        try:
            if self.crawl_type == "company_code":
                print(self.hy_type, " industry url: ", url)
                yield scrapy.Request(url=url, callback=self.process_hy_parse, headers=self.headers, meta={
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "ignore_https_errors": True,
                    },
                })
            elif self.crawl_type == "trade":
                session = scoped_session(self.sql_session)
                sql = "select code from company_code"
                results = session.execute(sql)
                print (results)
                headers = self.headers
                headers["Referer"] = "http://stockpage.10jqka.com.cn/"
                headers["Host"] = "d.10jqka.com.cn"
                for ret in results:
                    print("scrapy trade info for -", ret)
                    # trade_url = "http://stockpage.10jqka.com.cn/%s/" % (ret[0])
                    # yield scrapy.Request(url=trade_url, callback=self.process_stock_parse, headers=self.headers, cookies=self.cookies, meta={
                    #     "code": ret[0],
                    # })
                    time.sleep(1)
                    trade_url = "https://d.10jqka.com.cn/v2/realhead/hs_%s/last.js" % (ret[0])
                    print("scrapy url for -", trade_url)
                    yield scrapy.Request(url=trade_url, callback=self.process_stock_info_last, headers=headers, cookies=self.cookies, meta={
                        "code": ret[0],
                    })
                    # break
            elif self.crawl_type == "company":
                session = scoped_session(self.sql_session)
                sql = "select code from company_code"
                results = session.execute(sql)
                for ret in results:
                    code = ret[0]
                    company_url = "https://basic.10jqka.com.cn/%s/company.html#stockpage" % (code)
                    print ("company info url-", company_url)
                    yield scrapy.Request(url=company_url, callback=self.process_company_info_parse, headers=self.headers, cookies=self.cookies, meta={
                        "code": ret[0],
                    })
                    # break
                    time.sleep(0.5)
            elif self.crawl_type == "trade_history":
                session = scoped_session(self.sql_session)
                sql = "select code from company_code"
                results = session.execute(sql)
                for ret in results:
                    code = ret[0]
                    code = 688549
                    company_url = "https://d.10jqka.com.cn/v6/line/hs_%s/01/all.js" % (code)
                    print ("company info url-", company_url)
                    headers = self.headers
                    headers["Referer"] = "http://stockpage.10jqka.com.cn/"
                    yield scrapy.Request(url=company_url, callback=self.process_stock_history_parse, headers=headers, cookies=self.cookies, meta={
                        "code": ret[0],
                    })
                    break
                time.sleep(0.5)
        except Exception as e:
            traceback.print_exc()


    def process_hy_parse(self, response):
        # print (response.body.decode('gbk'))
        for index, group in enumerate(response.selector.xpath('//div[@class="cate_inner visible"]/div[@class="cate_group"]/div[@class="cate_items"]/a')):
            print("-------------------")
            try:
                url = group.xpath('@href').get().strip()
                hy_name = group.xpath('text()').get().strip()
                hy_code = url.split("detail")[1]
                print ("url-", url, "name-", hy_name, "hy_code - ", hy_code)
                time.sleep(0.5)
                yield scrapy.Request(url=url, callback=self.process_hy_page_parse, headers=self.headers, cookies=self.cookies, meta={
                    # "playwright": True,
                    # "playwright_context_kwargs": {
                    #     "ignore_https_errors": True,
                    # },
                    "hy_code": hy_code,
                    "url": url,
                    "hy_name": hy_name,
                })
                # break
            except Exception as e:
                traceback.print_exc()

    def process_hy_page_parse(self, response):
        hy_code = response.meta.get("hy_code", None)
        hy_name = response.meta.get("hy_name", None)
        page_info = response.selector.xpath('//div[@id="m-page"]/span[@class="page_info"]/text()').get()
        # url = response.meta["url"]
        if page_info is None:
            cur = 1
            page_num = 1
        else:
            cur,page_num = page_info.split("/")
            cur = int(cur)
            page_num = int(page_num)
        print ("cur page-", cur, "page num-", page_num)
        if self.hy_type == "zjh":
            url_page = "https://q.10jqka.com.cn/zjhhy/detail/field/199112/order/desc/page/%s/ajax/1%s"
        elif self.hy_type == "ths":
            url_page = "https://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/%s/ajax/1%s"
        else:
            return
        while cur <= page_num:
            url = url_page % (cur, hy_code)
            print ("scrapy url-", url, " page-", cur)
            try:
                # yield scrapy.Request(url=url, callback=self.process_stock_list_parse, meta={
                #     # "playwright": True,
                #     # "playwright_context_kwargs": {
                #     #     "ignore_https_errors": True,
                #     # },
                #     'splash':{
                #         'args':{
                #             'lua_source': script_hy_list_page,
                #             'page': cur,
                #             'wait': 20
                #         },
                #         'endpoint': 'execute',
                #     },
                #     "hy_code": hy_code,
                #     "hy_name": hy_name,
                # })
                yield scrapy.Request(url=url, callback=self.process_stock_list_parse, headers=self.headers, meta={
                    # "playwright": True,
                    # "playwright_context_kwargs": {
                    #     "ignore_https_errors": True,
                    # },
                    'splash':{
                        'args':{
                            'html': 1,
                            'wait': 3
                        },
                        'endpoint': 'render.html',
                    },
                    "hy_code": hy_code,
                    "hy_name": hy_name,
                })
                cur += 1
                # break
            except Exception as e:
                traceback.print_exc()
            time.sleep(1)
        pass

    def process_stock_list_parse(self, response):
        hy_code = response.meta.get("hy_code", None)
        hy_name = response.meta.get("hy_name", None)
        # print (response.body.decode('gbk'))
        # 获取所有股票代码
        # 翻页url： https://q.10jqka.com.cn/zjhhy/detail/field/199112/order/desc/page/2/ajax/1/code/B
        for index, group in enumerate(response.selector.xpath('//table[@class="m-table m-pager-table"]/tbody/tr')):
            # print (group.xpath('td'))
            url = group.xpath('td')[1].xpath('a/@href').get().strip()
            code = group.xpath('td')[1].xpath('a/text()').get().strip()
            print ("url - ", url, "code - ", code)
            try:
                if self.crawl_type == "company_code":
                    item = CompanyCodeItem()
                    item["db_name_"] = "stock_data"
                    item["table_name_"] = "company_code"
                    item["code"] = code
                    if self.hy_type == "zjh":
                        item["zjh_industry_code"] = hy_code.strip("/").split("/")[1]
                        item["zjh_industry_name"] = hy_name
                    elif self.hy_type == "ths":
                        item["ths_industry_code"] = hy_code.strip("/").split("/")[1]
                        item["ths_industry_name"] = hy_name
                    yield item
            except Exception as e:
                traceback.print_exc()
        # 获取页数/处理翻页,可能要执行js脚本
        pass

    def process_stock_parse(self, response):
        # print (response.body.decode('utf-8'))
        code = response.meta["code"]
        iframe_url = response.selector.xpath('//div[@class="new_detail fl"]/iframe/@src').get()
        print ("iframe url-", iframe_url)
        if iframe_url is None:
            return
        try:
            yield scrapy.Request(url=iframe_url, callback=self.process_stock_info_parse, dont_filter=True, meta={
                    'splash':{
                        'args':{
                            # 'html': 1,
                            'wait': 1,
                            'images': 0,
                        },
                        'endpoint': 'render.html',
                    },
                    # "playwright": True,
                    # "playwright_context_kwargs": {
                    #     "ignore_https_errors": True,
                    # },
                    "code": code,
                    "url": iframe_url,
                })
        except Exception as e:
            traceback.print_exc()

    def process_stock_info_parse(self, response):
        # body = gunzip(response.body)
        # print (response.body.decode('utf-8'))
        try:
            print ("process_stock_info_parse:", response.meta["url"])
            item = StockTradeInfoDayItem()
            item["db_name_"] = "stock_data"
            item["table_name_"] = "stock_trade_info_day"
            item["code"] = response.meta["code"]
            close_price = response.selector.xpath('//span[@id="hexm_curPrice"]/text()').get()
            item["cprice"] = close_price
            tdate = response.selector.xpath('//div[@class="minute_price_ztdt fl"]/p[@id="timeshow"]/text()').get()
            print ("-----tdate:", tdate)
            tdate = datetime.datetime.strptime(tdate, "%Y年%m月%d日 %H:%M:%S")
            item["tdate"] = tdate.strftime("%Y-%m-%d")
            for index, group in enumerate(response.selector.xpath('//div[@class="new_detail fl"]/ul[@class="new_trading fl"]/li/span')):
                print ("------", group.xpath('strong').get())
                dtype = group.xpath('strong/@id').get()
                value = None
                if dtype == "topenprice": #开盘价
                    value = group.xpath('strong/text()').get()
                    item["oprice"] = value
                elif dtype == "tamount": #成交量 转换
                    value = group.xpath('strong/text()').get()
                    unit = value[-1]
                    if unit == "万":
                        value = float(value[:-1]) * 10000
                    elif unit == "亿":
                        value = float(value[:-1]) * 100000000
                    item["tamount"] = value
                elif dtype == "trange": #振幅 %
                    value = group.xpath('strong/text()').get()
                elif dtype == "thighprice": #最高
                    value = group.xpath('strong/text()').get()
                    item["hprice"] = value
                elif dtype == "tamounttotal": #成交额 转换
                    value = group.xpath('strong/text()').get()
                    unit = value[-1]
                    if unit == "万":
                        value = float(value[:-1]) * 10000
                    elif unit == "亿":
                        value = float(value[:-1]) * 100000000
                    item["tprice"] = value
                elif dtype == "tchange": #换手率 %
                    value = group.xpath('strong/text()').get()
                    item["turnover"] = value[:-1]
                elif dtype == "tlowprice": #最低
                    value = group.xpath('strong/text()').get()
                    item["lprice"] = value
                elif dtype == "tvalue": #总市值 单位亿
                    value = group.xpath('strong/text()').get()
                    item["tvalue"] = value
                elif dtype == "tvaluep": #市净率
                    value = group.xpath('strong/text()').get()
                    item["pb"] = value
                elif dtype == "pprice": #昨收
                    value = group.xpath('strong/text()').get()
                elif dtype == "flowvalue": #流通市值 单位亿
                    value = group.xpath('strong/text()').get()
                    item["cvalue"] = value
                elif dtype == "fvaluep": # pe
                    value = group.xpath('strong/text()').get()
                    try:
                        value = float(value)
                    except:
                        value = -100
                    item["pe"] = "%s" % value
            print("stock info --- :", item)
            yield item
        except Exception as e:
            traceback.print_exc()

    def process_company_info_parse(self, response):
        try:
            # print (response.body.decode('gbk'))
            # hy_code = response.meta.get("hy_code", None)
            # hy_name = response.meta.get("hy_name", None)
            # if self.hy_type is None or hy_code is None or hy_name is None:
            #     return
            item = StockCompanyItem()
            # if self.hy_type == "zjh":
            #     item["zjh_industry_code"] = hy_code.strip("/").split("/")[1]
            #     item["zjh_industry_name"] = hy_name
            # elif self.hy_type == "ths":
            #     item["ths_industry_code"] = hy_code.strip("/").split("/")[1]
            #     item["ths_industry_name"] = hy_name
            brief_info = response.selector.xpath('//div[@class="bd"]/table[@class="m_table"]/tbody/tr')
            print ("brief info: ", brief_info)
            # brief_info[0].xpath('td')[1].xpath('strong/text()')
            item["code"] = response.meta["code"]
            item["name"] = brief_info[0].xpath('td')[1].xpath('span/text()').get()
            item["region"] = brief_info[0].xpath('td')[2].xpath('span/text()').get()
            item["ename"] = brief_info[1].xpath('td')[0].xpath('span/text()').get()
            item["sw_industry_name"] = brief_info[1].xpath('td')[1].xpath('span/text()').get()
            item["oname"] = brief_info[2].xpath('td')[0].xpath('span/text()').get()
            netaddr = brief_info[2].xpath('td')[1].xpath('span/text()').get()
            # details_body = response.selector.xpath('//div[@class="bd"]/div[@class="m_tab_content2"]/table[@class="m_table ggintro managelist"]/tbody')
            # print ("0000000000000000", details_body.get())
            details = response.selector.xpath('//div[@class="bd"]/div[@class="m_tab_content2"]/table[@class="m_table ggintro managelist"]/tbody/tr')
            # print ("details: ", len(details), details)
            item["main_business"] = details[0].xpath('td/span/text()').get()
            product_name = details[1].xpath('td/span/text()').get()
            item["chairman"] = details[4].xpath('td/span/a/text()').get()
            item["CEO"] = details[5].xpath('td/span/a/text()').get()
            registered_capital=details[5].xpath('td')[1].xpath('span/text()').get().strip()
            uint = registered_capital[-1]
            # if uint == "万":
            #     registered_capital = float(registered_capital[:-1]) * 10000
            # elif uint == "亿":
            #     registered_capital = float(registered_capital[:-1]) * 100000000
            item["registered_capital"] = registered_capital
            item["no_employees"] = details[5].xpath('td')[2].xpath('span/text()').get()
            item["address"] = details[7].xpath('td/span/text()').get()
            item["intro"] = details[8].xpath('td/p/text()').get()
            item["table_name_"] = "company"
            item["db_name_"] = "stock_data"

            # for d in details:
            #     print ("-----------------------------------")
            #     print (d.get())

            print ("company info-", item)
            yield item
        except Exception as e:
            traceback.print_exc()

    def process_stock_history_parse(self, response):
        # body = gunzip(response.body)
        print (response.body.decode('utf-8'))
        body = response.body.decode('utf-8')
        begin = body.find('{')
        end = body.rfind('}')
        jsonstr = body[begin:end+1]
        # print (jsonstr)
        try:
            all_json = json.loads(jsonstr)
            print (all_json)
            total = int(all_json["total"])
            start_date = all_json["start"]
            price_factor = all_json["priceFactor"]
            # 四个数字一组：最低价，开盘价，最高价，收盘价
            prices = all_json["price"].strip().split(",")
            volumns = all_json["volumn"].strip().split(",")
            dates = all_json["dates"].strip().split(",")
            sort_years = all_json["sortYear"]
            full_dates = []
            date_idx = 0
            for year_item in sort_years:
                year,count = year_item
                print (year, count)
                for i in range(1, count+1):
                    full_dates.append(str(year) + dates[date_idx])
                    date_idx += 1
            print ("all dates:", full_dates)

            if 4*len(full_dates) != len(prices):
                print ("[error]: dates count", len(full_dates), "and prices count", len(prices),"not match")
                return
            if len(full_dates) != len(volumns):
                print ("[error]: dates count", len(full_dates), "and volumns count", len(volumns),"not match")
                return
            for i in range(0, len(full_dates)):
                d = full_dates[i]
                # item = StockTradeInfoDayItem()
                # item["hprice"] = 
                # item["lprice"] = value
                # item["oprice"] = value
                # item["cprice"] = value
                # item["tamount"] = value
                # print("stock info --- :", item)
                # yield item
        except Exception as e:
            traceback.print_exc()

    def process_stock_info_last(self, response):
        # body = gunzip(response.body)
        # print (response.body.decode('utf-8'))
        try:
            # print ("process_stock_info_parse:", response.meta["url"])
            body = response.body.decode("utf-8")
            begin = body.find('{')
            end = body.rfind('}')
            jsonstr = body[begin:end+1]
            all_json = json.loads(jsonstr)
            result = all_json["items"]
            print (jsonstr)
            item = StockTradeInfoDayItem()
            item["db_name_"] = "stock_data"
            item["table_name_"] = "stock_trade_info_day"
            item["code"] = result["5"]
            item["cprice"] = result["10"] # 收盘价
            item["tdate"] = result["updateTime"].strip().split(" ")[0]
            item["oprice"] =  result["7"] #开盘价
            item["tamount"] = result["13"] #成交量
            item["hprice"] = result["8"]  #最高
            item["tprice"] = result["19"]  #成交额
            item["turnover"] = result["1968584"]  #换手率 %
            item["lprice"] = result["9"] #最低
            item["tvalue"] = result["3541450"] #总市值
            if result["592920"] == "":
                item["pb"] = "-100"
            else:
                item["pb"] = result["592920"]
            item["cvalue"] = result["3475914"] #流通市值
            if result["2942"] == "":
                item["pe"] = "-100"
            else:
                item["pe"] = "%s" % result["2942"]
                    
            print("stock info --- :", item)
            yield item
        except Exception as e:
            traceback.print_exc()
