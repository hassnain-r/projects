# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item,Field


class DocketsItem(Item):
    description = Field()
    assinges = Field()
    filled_by = Field()
    filling_date = Field()
    filled__by = Field()
    title = Field()
    extenshion = Field()
    sourse_url = Field()

    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
