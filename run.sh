#!/bin/bash
cd /home/stock/shooter
#conda activate scrapy
echo "scrapy begin stock-market"
scrapy crawl StockMarket -a crawl_type=trade
