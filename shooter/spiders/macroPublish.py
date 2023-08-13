import scrapy
from playwright.async_api import async_playwright
from scrapy.utils.project import get_project_settings
import time
from datetime import datetime

from shooter.items import MacroPubNoticeItem

settings = get_project_settings()

class MacropublishSpider(scrapy.Spider):
    name = "macroPublish"
    allowed_domains = ["www.stats.gov.cn"]
    start_urls = ["http://www.stats.gov.cn/"]
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Referer":"http://www.stats.gov.cn/",
        "Host":"data.stats.gov.cn",
    }
    def start_requests(self):
        url = "http://www.stats.gov.cn/"
        yield scrapy.Request(url=url, callback=self.extract_html_parse, meta={
                "playwright": True,
                "playwright_context_kwargs": {
                    "ignore_https_errors": True,
                },
            })

    def extract_html_parse(self, response):
        # print(response.body.decode())
        # with open("stat.html","w+") as fp:
        #     fp.write(response.body.decode())
        for index, item in enumerate(response.selector.xpath('//div[@class="wrapper-content4-right-scroll-item"]')):
            sdate = item.xpath('//div[@class="wrapper-content4-right-content"]/div[@class="wrapper-content4-right-date"]/span/text()').get().strip()
            contents = item.xpath('//div[@class="fbyg-item"]/ul/li/a/text()').getall()
            print("-----------------------")
            # 7月15日 周六 9:30
            print(sdate)
            ti = time.localtime()
            d,w,t = sdate.split(' ')
            s = "%d-%s %s" % (ti.tm_year, d, t)
            t = datetime.strptime(s, '%Y-%m月%d日 %H:%M')
            for ctxt in contents:
                ctxt = ctxt.strip()
                item = MacroPubNoticeItem()
                item["table_name_"] = "macro_publish_notice"
                item["db_name_"] = "macro_data"
                item["content"] = ctxt
                item["publish_date"] = t.strftime('%Y-%m-%d')
                item["publish_datetime"] = t.strftime('%Y-%m-%d %H:%M:%S')
                yield item
