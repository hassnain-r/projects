from __future__ import absolute_import
import scrapy
import time
import json
import datetime
from cymoda.items import CymodaItem
import delay


class CymodaData(scrapy.Spider):
    name = "canada-mx-crawl"
    start_urls = ["http://www.cyamoda.com/"]

    def parse(self, response):
        starting_page = response.xpath('.//ul[@class="first"]//a/@href').extract_first()
        starting_page_link = "http://www.cyamoda.com/" + starting_page
        yield scrapy.Request(url=starting_page_link, callback=self.parse_categories_urls)

    def parse_categories_urls(self, response):
        sub_categories = response.xpath('.//a[@class="menu-item-texto"]/@href').extract()
        for each_url_keyword in sub_categories:
            each_url = "http://www.cyamoda.com"+each_url_keyword
            yield scrapy.Request(url=each_url, callback=self.parse_sub_cat_urls)

    def parse_sub_cat_urls(self, response):
        sub_cat_pages = response.xpath('.//a[@class="product-image wow slideInUp"]/@href').extract()
        for each_page in sub_cat_pages:
            yield scrapy.Request(url=each_page, dont_filter=True, callback=self.parse_data)


    def parse_data(self, response):
        item = CymodaItem()
        unicode_content = response.xpath('.//script[@language="javascript"]/text()').extract_first()
        str_content = unicode_content.encode('utf8')
        start_point = str_content.find("RegionName") + 13
        end_point = str_content.find('"', start_point)
        market = str_content[start_point:end_point]
        item["market"] = market
        item["gender"] = "women"
        item["category"] = response.xpath('.//div[@class="bread-crumb"]//a/text()').extract()
        item["brand"] = response.xpath('.//a[@class="logo"]/text()').extract_first()
        item["brand_name"] = response.xpath('.//h1//div/text()').extract_first()
        item["description"] = response.xpath('.//div[@class="productDescription"]/text()').extract()
        item["spider_name"] = self.name
        item["lang"] = response.xpath('.//meta[@name="language"]/@content').extract_first()
        item["crawl_start_time"] = time.asctime(time.localtime(time.time()))
        item["date"] = time.time()

        image_urls_uni_content = response.xpath('.//input[@id="___rc-p-sku-ids"]/@value').extract_first()
        id_led__to_json_content = response.xpath('.//input[@id="___rc-p-id"]/@value').extract_first()
        if image_urls_uni_content:
            str_content = image_urls_uni_content.encode('utf8')
            starting_point = str_content.find("'") + 1
            ending_point = str_content.find(',', starting_point)
            images_id = str_content[starting_point:ending_point]
            image_urls_page = "https://alma.engranedigital.com/web_assets/api/getStock.php?id=" + images_id
            yield scrapy.Request(url=image_urls_page, meta={'item': item, "json_content": id_led__to_json_content}, callback=self.parse_images_content)

    def parse_images_content(self, response):
        item = response.meta['item']
        json_data = response.body
        json_content = json.loads(json_data)
        images_urls_list = []
        images_urls = json_content["Images"]
        for i in images_urls:
            images_urls_list.append(i['ImageUrl'])
        item["image_urls"] = images_urls_list
        item["uuid"] = json_content["CSCIdentification"]
        id_led__to_json_content = response.meta["json_content"]
        if id_led__to_json_content:
            json_content_page = "https://alma.engranedigital.com/web_assets/api/getVariations.php?id=" + \
                                id_led__to_json_content
            yield scrapy.Request(url=json_content_page, meta={'item': item}, callback=self.parse_skus_content)

    def parse_skus_content(self, response):
        item = response.meta["item"]
        json_data = response.body
        json_content = json.loads(json_data)
        final_list = []
        list_having_values = json_content["skus"]
        item["retailer_sku"] = json_content["productId"]
        for i in list_having_values:
            my_dict = {}
            my_dict["sku_id"] = i["sku"]
            my_dict["price"] = i["bestPrice"]
            my_dict["currency"] = "MXN"

            size_color_dict = i["dimensions"]
            for key, value in size_color_dict.items():
                if value:
                    my_dict[key] = value
            final_list.append(my_dict)
        item["skuss"] = final_list
        yield item
