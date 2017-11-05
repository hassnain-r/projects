# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class DarazItem(Item):
    All_categories = Field()
    category_name = Field()
    key_features = Field()
    final_price = Field()
    old_price = Field()
    description = Field()
    delivery_info = Field()
    brand_name = Field()
    image_urls = Field()
    percentage_discount = Field()
    path_leads_to_product = Field()
    available_sizes = Field()

    # define the fields for your item here like:
    # name = scrapy.Field()
    pass