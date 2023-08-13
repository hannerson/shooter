import scrapy
# from playwright.async_api import async_playwright
from scrapy.utils.project import get_project_settings
import time
import datetime

from shooter.items import StockCompanyItem, StockTradeInfoDayItem

script_hy_list_page = """
function main(splash, args)
    splash.images_enabled = false
    assert(splash:go(args.url))
    assert(splash:wait(1))
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
        # "Referer": "http://q.10jqka.com.cn/zjhhy/detail/code/B/",
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

    def start_requests(self):
        urls = [
            "http://q.10jqka.com.cn/zjhhy/",
            # "http://q.10jqka.com.cn/thshy/",
            ]
        for url in urls:
            time.sleep(1)
            yield scrapy.Request(url=url, callback=self.process_hy_parse, meta={
                "playwright": True,
                "playwright_context_kwargs": {
                    "ignore_https_errors": True,
                },
            })

    def process_hy_parse(self, response):
        # print (response.body.decode('gbk'))
        
        page_num = 1
        hy_list_pre_url = "https://q.10jqka.com.cn/zjhhy/detail/field/199112/order/desc/page/1/ajax/1"
        for index, group in enumerate(response.selector.xpath('//div[@class="cate_inner visible"]/div[@class="cate_group"]/div[@class="cate_items"]/a')):
            print("-------------------")
            url = group.xpath('@href').get().strip()
            hy_name = group.xpath('text()').get().strip()
            hy_code = url.split("detail")[1]
            # for i,item in enumerate(group.xpath('//div[@class="cate_group"]/div[@class="cate_items"]/a')):    
            #     print(item.xpath('/@href').getall())
            # url = "http://q.10jqka.com.cn/zjhhy/detail/code/Q/"
            print ("url-", url, "name-", hy_name, "hy_code - ", hy_code)
            #翻页url： https://q.10jqka.com.cn/zjhhy/detail/field/199112/order/desc/page/1/ajax/1/code/B
            # hy_list_url = hy_list_pre_url + hy_code
            # print ("request-url : ", hy_list_url)
            time.sleep(1)
            yield scrapy.Request(url=url, callback=self.process_hy_page_parse, headers=self.headers, cookies=self.cookies, meta={
                # "playwright": True,
                # "playwright_context_kwargs": {
                #     "ignore_https_errors": True,
                # },
                "hy_code": hy_code,
                "url": url,
            })
            # yield scrapy.Request(url=url, callback=self.process_hy_page_parse, meta={
            #     'splash':{
            #         'args':{
            #             'html':1,
            #             'png':1,
            #         },
            #         'endpoint': 'render.json',
            #     }
            # })
            break

    def process_hy_page_parse(self, response):
        page_info = response.selector.xpath('//div[@id="m-page"]/span[@class="page_info"]/text()').get()
        url = response.meta["url"]
        if page_info is None:
            cur = 1
            page_num = 1
        else:
            cur,page_num = page_info.split("/")
            cur = int(cur)
            page_num = int(page_num)
        print ("cur page-", cur, "page num-", page_num)
        while cur <= page_num:
            print ("scrapy url-", url, " page-", cur)
            yield scrapy.Request(url=url, callback=self.process_stock_list_parse, meta={
                'splash':{
                    'args':{
                        'lua_source': script_hy_list_page,
                        'page': cur,
                        'wait': 10
                    },
                    'endpoint': 'execute',
                }
            })
            cur += 1
            break
        pass

    def process_stock_list_parse(self, response):
        # print (response.body.decode('gbk'))
        # 获取所有股票代码
        # 翻页url： https://q.10jqka.com.cn/zjhhy/detail/field/199112/order/desc/page/2/ajax/1/code/B
        for index, group in enumerate(response.selector.xpath('//table[@class="m-table m-pager-table"]/tbody/tr/td/a')):
            url = group.xpath('@href').get().strip()
            code = group.xpath('text()').get().strip()
            print ("url - ", url, "code - ", code)
            # 跳转到股票个股页
            yield scrapy.Request(url=url, callback=self.process_stock_parse, meta={
                'splash':{
                    'args':{
                        'html': 1,
                        'wait': 10
                    },
                    'endpoint': 'render.html',
                },
                "code": code,
            })
            # 跳转到公司介绍页 url + "/company/"
            # https://basic.10jqka.com.cn/300483/company.html#stockpage
            company_url = "https://basic.10jqka.com.cn/%s/company.html#stockpage" % (code)
            print ("company info url-", company_url)
            yield scrapy.Request(url=company_url, callback=self.process_company_info_parse, headers=self.headers, cookies=self.cookies, meta={
                # 'splash':{
                #     'args':{
                #         'html': 1,
                #         'wait': 10
                #     },
                #     'endpoint': 'render.html',
                # }
                # "playwright": True,
                # "playwright_context_kwargs": {
                #     "ignore_https_errors": True,
                # },
                "code": code,
            })
            break
        # 获取页数/处理翻页,可能要执行js脚本
        pass

    def process_stock_parse(self, response):
        # print (response.body.decode('utf-8'))
        code = response.meta["code"]
        iframe_url = response.selector.xpath('//div[@class="new_detail fl"]/iframe/@src').get()
        print ("iframe url-", iframe_url)
        yield scrapy.Request(url=iframe_url, callback=self.process_stock_info_parse, meta={
                'splash':{
                    'args':{
                        'html': 1,
                        'wait': 10
                    },
                    'endpoint': 'render.html',
                },
                "code": code,
            })

    def process_stock_info_parse(self, response):
        # print (response.body.decode('utf-8'))
        item = StockTradeInfoDayItem()
        item["db_name_"] = "stock_data"
        item["table_name_"] = "stock_trade_info_day"
        close_price = response.selector.xpath('//span[@id="hexm_curPrice"]/text()').get()
        item["cprice"] = close_price
        tdate = response.selector.xpath('//div[@class="minute_price_ztdt fl"]/p[@id="timeshow"]/text()').get()
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
                item["pe"] = value
        print("stock info --- :", item)
        # yield item

    def process_company_info_parse(self, response):
        # print (response.body.decode('gbk'))
        item = StockCompanyItem()
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
        registered_capital=details[5].xpath('td')[1].xpath('span/text()').get().strip().strip("元")
        uint = registered_capital[-1]
        if uint == "万":
            registered_capital = float(registered_capital[:-1]) * 10000
        elif uint == "亿":
            registered_capital = float(registered_capital[:-1]) * 100000000
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

