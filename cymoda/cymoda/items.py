# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class CymodaItem(scrapy.Item):
    trial = Field()
    gender = Field()
    market = Field()
    category = Field()
    brand = Field()
    brand_name = Field()
    description = Field()
    image_urls = Field()
    skuss = Field()
    spider_name = Field()
    crawl_start_time = Field()
    date = Field()
    uuid = Field()
    retailer_sku = Field()
    lang = Field()
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
