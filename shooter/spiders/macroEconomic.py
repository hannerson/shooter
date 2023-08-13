import scrapy
from urllib.parse import urlparse
from urllib.parse import urlencode
import json
from scrapy_splash import SplashRequest
# from scrapy_selenium import SeleniumRequest
from playwright.async_api import async_playwright
from scrapy.utils.project import get_project_settings
import time
import datetime
from shooter.items import MacroStatDataItem

lua_script = """
	function main(splash, args)
		splash:go(args.url)
		splash:wait(args.wait)
		return splash:html()
	end
	"""
settings = get_project_settings()

class MacroeconomicSpider(scrapy.Spider):
    name = 'macroEconomic'
    allowed_domains = ['data.stats.gov.cn']
    start_urls = ['https://data.stats.gov.cn/']
    filter_subpath = ["/easyquery.htm", "/tablequery.htm"]
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Referer":"http://www.stats.gov.cn/",
        "Host":"data.stats.gov.cn",
    }
    url_prefix = "https://data.stats.gov.cn/easyquery.htm"
    macro_data_conf = settings.get("MACRO_DATA_CONF")
    # https://data.stats.gov.cn/easyquery.htm
    # 居民消费价格指数CPI A010101-上年同月, A010201-上年同期, A010301-上月 01-居民全部 02-食品烟酒类 03-衣着类 03-居住类 04-生活用品服务类
    # 工业生产者购进价格指数PPI A010701-上年同月, A010702-上年同期，A010703-上月
    # 房地产投资开发投资 (Real estate development and investment) REDI A0601
    # 制造业采购经理指数PMI-A0B01 非制造业采购经理指数-A0B02 综合PMI产出指数-A0B03
    # 国家财政预算收入 State Budgetary Revenues -A0C01 国家财政预算支出 State Budgetary Expenditure-A0C02
    # "https://data.stats.gov.cn/easyquery.htm?cn=A01", #月度数据
    # "https://data.stats.gov.cn/easyquery.htm?cn=B01", #季度数据
    # "https://data.stats.gov.cn/easyquery.htm?cn=C01", #年度数据
    # https://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgyd&rowcode=zb&colcode=sj&wds=[]&dfwds=[{"wdcode":"sj","valuecode":"LAST36"}]
    # https://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgyd&rowcode=zb&colcode=sj&wds=[]&dfwds=[{"wdcode":"zb","valuecode":"A010101"}]&k1=1689258373758&h=1
    # https://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgyd&rowcode=zb&colcode=sj&wds=[]&dfwds=[{"wdcode":"zb","valuecode":"A010201"}]&k1=1689258575825&h=1
    def start_requests(self):
        valuecodes = [
            "A010101", # CPI
            "A010201", # CPI
            "A010301", # CPI
            "A010701", # PPI
            "A0B01", # PMI
            "A0B02", # PMI
            "A0B03", # PMI
            "A0D01", # M0 M1 M2
        ]
        for code in valuecodes:
            # yield SplashRequest(url=url, callback=self.extract_data_parse, endpoint='execute', 
            #                     args={'lua_source':lua_script, 'wait':5, 'html':1,'png':1, 'width':1000,},
            #                     meta={'splash': {'args': {'headers': self.headers}}})
            # yield SeleniumRequest(url=url, callback=self.extract_data_parse, meta={'playwright': True})
            paramters = {
                "m":"QueryData",
                "dbcode":"hgyd",
                "rowcode":"zb",
                "colcode":"sj",
                "wds":"[]",
                "h":"1",
            }
            paramters["dfwds"] = "[{\"wdcode\":\"zb\",\"valuecode\":\"%s\"}]" % (code)
            paramters["k1"]  = int(round(time.time() * 1000))
            url = "%s?%s" % (self.url_prefix, urlencode(paramters))
            print (url)
            # yield scrapy.Request(url=url, callback=self.extract_json_parse, meta={
            #     "playwright": True,
            #     "playwright_context_kwargs": {
            #         "ignore_https_errors": True,
            #     },
            # })
            time.sleep(1)
            yield scrapy.Request(url=url, callback=self.extract_json_parse)


    def extract_json_parse(self, response):
        jdata = json.loads(response.body.decode())
        # print (jdata)
        # return {"url":response.url}
        print(settings.get("MACRO_DATA_CONF"))
        if "returncode" in jdata and jdata["returncode"] == 200:
            for data in jdata["returndata"]["datanodes"]:
                scode = data["code"]
                if not data["data"]["hasdata"]:
                    continue
                (zbcode, sjcode) = scode.split('_')
                code = zbcode.split('.')[-1]
                dcode = sjcode.split('.')[-1]
                if not code in self.macro_data_conf:
                    print ("no such defination for this code: ", code)
                    continue
                print (self.macro_data_conf[code])
                item = MacroStatDataItem()
                item["table_name_"] = "macro_stat_data"
                item["db_name_"] = "macro_data"
                item["name"] = "%s-%s" % (self.macro_data_conf[code]["name"], self.macro_data_conf[code]["subname"])
                item["type"] = self.macro_data_conf[code]["type"]
                item["stype"] = self.macro_data_conf[code]["stype"]
                item["stat_type"] = self.macro_data_conf[code]["stat_type"]
                item["stat_date"] = "%s01" % dcode
                item["value"] = data["data"]["data"]
                yield item


    def extract_html_parse(self, response):
        # print(response.body)
        for url in response.css('a'):
            if 'href' in url.attrib:
                url_result = urlparse(url.attrib['href'])
                if url_result.path not in self.filter_subpath:
                    continue
                print("url ----- ", url.attrib['href'])
                print(url_result)
        # print(url.attrib['href'] for url in response.css('a'))
