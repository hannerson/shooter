import scrapy

from scrapy.utils.project import get_project_settings
import time
import datetime
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
import json
import re

from shooter.items import CompanyCodeItem, StockCompanyItem, StockTradeInfoDayItem

# 1. 交易历史数据(包括pe/pb等)
# 2. 市场整体估值/行业估值
#
#

class EastmoneySpider(scrapy.Spider):
    name = "EastMoney"
    allowed_domains = ["data.eastmoney.com"]
    start_urls = ["http://data.eastmoney.com/"]

    cookies = {
        "qgqp_b_id":"a862276c16d674c99041f29a75c8d457",
        "websitepoptg_show_time":"1693924595523",
        "st_si":"94116997084264",
        "websitepoptg_api_time":"1694338596991",
        "st_asi":"delete",
        "HAList":"ty-0-300059-%u4E1C%u65B9%u8D22%u5BCC%2Cty-1-688549-N%u4E2D%u5DE8%u82AF-U%2Cty-0-831010-%u51EF%u6DFB%u71C3%u6C14%2Cty-90-BK0733-%u5305%u88C5%u6750%u6599%2Cty-1-000001-%u4E0A%u8BC1%u6307%u6570%2Cty-0-301299-%u5353%u521B%u8D44%u8BAF%2Cty-0-002701-%u5965%u745E%u91D1%2Cty-0-002095-%u751F%20%u610F%20%u5B9D%2Cty-105-AAPL-%u82F9%u679C%2Cty-106-BAC-%u7F8E%u56FD%u94F6%u884C",
        "JSESSIONID":"2F1A6FB7F96CD19959E1EE0FD43E4F6F",
        "st_pvi":"06771012069214",
        "st_sp":"2023-07-20%2023%3A18%3A57",
        "st_inirUrl":"https%3A%2F%2Fwww.baidu.com%2Flink",
        "st_sn":"19",
        "st_psi":"20230910180118146-113300303061-5691848092",
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "datacenter-web.eastmoney.com",
        "Referer": "https://data.eastmoney.com/gzfx/scgk.html",
        "Sec-Fetch-Dest": "script",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
    }

    settings = get_project_settings()
    db_engine = create_engine("mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (settings.get("MYSQL_USER"),
            settings.get("MYSQL_PASSWORD"), settings.get("MYSQL_HOST"), settings.get("MYSQL_PORT"),
            settings.get("MYSQL_STOCK_DB_NAME"), settings.get("MYSQL_CHARSET")), pool_size=5, pool_timeout=30)
    sql_session = sessionmaker(bind=db_engine)

    crawl_type = "trade" # trade/valuation (交易数据/估值数据)
    trade_type = None # last/history
    valuation_type = None # individual/market
    begin_date = None
    end_date = None

    def is_valid_date(self, date_str):
        date_format = "%Y-%m-%d"
        try:
            datetime.datetime.strptime(date_str, date_format)
            return True
        except ValueError:
            return False

    def start_requests(self):
        if self.crawl_type not in ["trade","valuation"]:
            print ("[error]: crawl_type must be [trade|valuation]")
            return
        if self.crawl_type == "valuation":
            if self.valuation_type not in ["individual","market"]:
                print ("[error]: valuation_type must be [individual|market]")
                return
            if self.begin_date is None or self.end_date is None:
                print ("[error]: begin_date and end_date must not be None and like 2023-09-10")
                return
            # check date format: 2023-09-10
            if not self.is_valid_date(self.begin_date) or not self.is_valid_date(self.end_date):
                print ("[error]: begin_date and end_date must not be None and like 2023-09-10")
                return
            begin_date = datetime.datetime.strptime(self.begin_date, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(self.end_date, "%Y-%m-%d")

            if begin_date > end_date:
                print ("[error]: end_date must be bigger than begin_date")
                return
            if self.valuation_type == "individual":
                url_fmt = "https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery1123028900285380891777_1694343082182&sortColumns=SECURITY_CODE&sortTypes=1&pageSize=50&pageNumber={0}&reportName=RPT_VALUEANALYSIS_DET&columns=ALL&quoteColumns=&source=WEB&client=WEB&filter=(TRADE_DATE%3D%27{1}%27)"
                page_num = 1
                cur_date = begin_date
                while cur_date <= end_date:
                    url = url_fmt.format(page_num, cur_date.strftime("%Y-%m-%d"))
                    print ("crawl url : ", url)
                    yield scrapy.Request(url=url, callback=self.parse_total_page, headers=self.headers, cookies=self.cookies, dont_filter=True, meta={
                        "cur_date": cur_date
                    })
                    time.sleep(1)
                    cur_date = cur_date + datetime.timedelta(days=1)
            elif self.valuation_type == "market":
                pass
        elif self.crawl_type == "trade":
            if self.trade_type not in ["last","history"]:
                print ("[error]: trade_type must be [last|history]")
                return
            
            if self.trade_type == "history":
                headers = self.headers
                headers["Referer"] =  "http://quote.eastmoney.com/"
                headers["Host"] = "push2his.eastmoney.com"
                url_fmt = "http://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&ut=fa5fd1943c7b386f172d6893dbfba10b&rtntype=6&secid={0}.{1}&klt=101&fqt=1&cb=jsonp1694529994138"
                session = scoped_session(self.sql_session)
                sql = "select code from company_code"
                results = session.execute(sql)
                pattern = r'^6'
                market_type = 0
                for ret in results:
                    code = ret[0]
                    if re.match(pattern, code):
                        market_type = 1
                    else:
                        market_type = 0
                    url = url_fmt.format(market_type, code)
                    print ("crawl url : ", url)
                    yield scrapy.Request(url=url, callback=self.parse_stock_trade_history, headers=headers, cookies=self.cookies, meta={
                    })
                    # break
                    time.sleep(1)
            elif self.trade_type == "last":
                pass

    def parse_total_page(self, response):
        body = response.body.decode("utf-8")
        cur_date = response.meta.get("cur_date")
        begin = body.find('{')
        end = body.rfind('}')
        jsonstr = body[begin:end+1]
        print (jsonstr)
        try:
            all_json = json.loads(jsonstr)
            print (all_json)
            result = all_json["result"]
            if result is None:
                return
            page_total = result.get("pages", None)
            page_cur = 1
            url_fmt = "https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery1123028900285380891777_1694343082182&sortColumns=SECURITY_CODE&sortTypes=1&pageSize=50&pageNumber={0}&reportName=RPT_VALUEANALYSIS_DET&columns=ALL&quoteColumns=&source=WEB&client=WEB&filter=(TRADE_DATE%3D%27{1}%27)"
            while page_cur <= page_total:
                url = url_fmt.format(page_cur, cur_date.strftime("%Y-%m-%d"))
                yield scrapy.Request(url=url, callback=self.parse_individual_stock, headers=self.headers, cookies=self.cookies, dont_filter=True, meta={
                    "cur_date": cur_date
                })
                time.sleep(1)
                page_cur += 1
                # break
        except Exception as e:
            print (e)
            traceback.print_exc()

    def parse_individual_stock(self, response):
        body = response.body.decode("utf-8")
        begin = body.find('{')
        end = body.rfind('}')
        jsonstr = body[begin:end+1]
        cur_date = response.meta.get("cur_date")
        print (jsonstr)
        try:
            all_json = json.loads(jsonstr)
            print (all_json)
            result = all_json["result"]
            page_total = result.get("pages", None)
            data = result["data"]
            for d in data:
                item = StockTradeInfoDayItem()
                item["db_name_"] = "stock_data"
                item["table_name_"] = "stock_trade_info_day"
                item["code"] = d["SECURITY_CODE"]
                item["tdate"] = d["TRADE_DATE"].split(" ")[0]
                item["pb"] = d["PB_MRQ"]
                item["cprice"] = d["CLOSE_PRICE"]
                item["tvalue"] = d["TOTAL_MARKET_CAP"]
                item["cvalue"] = d["NOTLIMITED_MARKETCAP_A"]
                item["pe"] = d["PE_TTM"]
                item["total_share"] = d["TOTAL_SHARES"]
                item["free_share"] = d["FREE_SHARES_A"]
                item["peg"] = d["PEG_CAR"]
                item["pe_lyr"] = d["PE_LAR"]
                item["ps_ttm"] = d["PS_TTM"]
                item["pcf_ocf_ttm"] = d["PCF_OCF_TTM"]
                yield item
        except Exception as e:
            print (e)
            traceback.print_exc()

    def parse_stock_trade_history(self, response):
        body = response.body.decode("utf-8")
        begin = body.find('{')
        end = body.rfind('}')
        jsonstr = body[begin:end+1]
        print (jsonstr)
        try:
            all_json = json.loads(jsonstr)
            print (all_json)
            result = all_json["data"]
            code = result.get("code", "")
            name = result.get("name", "")
            data = result["klines"]
            with open("data/%s.txt" % (code), mode="w+", encoding="utf-8") as f:
                for d in data:
                    f.write("%s,%s,%s\n" % (code, name, d.strip()))
                    # d_arr = d.strip().split(",")
                    # item = StockTradeInfoDayItem()
                    # item["db_name_"] = "stock_data"
                    # item["table_name_"] = "stock_trade_info_day"
                    # item["code"] = code
                    # item["name"] = name
                    # item["tdate"] = d_arr[0]
                    # item["oprice"] = d_arr[1]
                    # item["cprice"] = d_arr[2]
                    # item["hprice"] = d_arr[3]
                    # item["lprice"] = d_arr[4]
                    # item["tamount"] = d_arr[5]
                    # item["tprice"] = d_arr[6]
                    # item["amplitude"] = d_arr[7]
                    # item["change_rate"] = d_arr[8]
                    # item["change"] = d_arr[9]
                    # item["turnover"] = d_arr[10]
                    # time.sleep(0.1)
                    # yield item
                f.close()
        except Exception as e:
            print (e)
            traceback.print_exc()
