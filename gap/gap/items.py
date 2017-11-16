# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class GapItem(scrapy.Item):
    url = Field()
    refer_url = Field()
    brand_Name = Field()
    new_base_Url = Field()
    new_price_text = Field()
    title = Field()
    country_code = Field()
    color = Field()
    timestamp = Field()
    currency = Field()
    image_url = Field()
    description = Field()
    old_price_text = Field()
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
