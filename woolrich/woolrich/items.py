# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class WoolrichItem(scrapy.Item):
    title = Field()
    Currency = Field()
    url_original = Field()
    url = Field()
    timestamp = Field()
    description = Field()
    selected_size = Field()
    brand_name = Field()
    requests = Field()
    category = Field()
    currency = Field()
    color_name = Field()
    care = Field()
    new_price = Field()
    skus = Field()
    image_urls = Field()
    old_price = Field()

    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
