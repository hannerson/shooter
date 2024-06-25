#!/bin/bash
cd /home/stock/shooter
#conda activate scrapy
echo "scrapy begin eastmoney"
cur_date=`date +%Y-%m-%d`
echo "$cur_date"

scrapy crawl EastMoney -a crawl_type=valuation -a valuation_type=individual -a begin_date=$cur_date -a end_date=$cur_date
