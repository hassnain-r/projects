from __future__ import absolute_import
import scrapy
import json
import time
import re
from gap.items import GapItem


class GapProducts(scrapy.Spider):
    name = "gap.com_extractor"
    countries_list = []

    def __init__(self, countries="", **kwargs):
        super(GapProducts, self).__init__(**kwargs)
        self.start_urls = [
            'http://www.gap.com/',
        ]
        self.countries = "%s" % countries
        self.countries = countries.split(',')
        for country_code in self.countries:
            self.countries_list.append(country_code)

    def parse(self, response):
        for country_code in self.countries_list:
            requested_country_url = "https://secure-www.gap.com/resources/shippingOptions/v1/" + country_code
            yield scrapy.Request(url=requested_country_url, dont_filter=True, callback=self.parse_new_base_url)

    def req_country_data(self, response):
        req_country_json_content = json.loads(response.body)
        return req_country_json_content

    def get_country_code(self, response):
        req_country_json_content = self.req_country_data(response)
        country_code = req_country_json_content["shippingOptionsInfo"]["requestedShippingCountryCode"]
        return country_code

    def get_currency(self, response):
        req_country_json_content = self.req_country_data(response)
        currency = req_country_json_content["shippingOptionsInfo"].get("availableNativeShippingCountry")
        if currency is not None:
            return currency.get("currencyCode")
        else:
            return req_country_json_content["shippingOptionsInfo"]["availableGlobalShippingCountry"]["currencyCode"]

    def parse_new_base_url(self, response):
        item = GapItem()
        item["country_code"] = self.get_country_code(response)
        item["currency"] = self.get_currency(response)
        req_country_json_content = self.req_country_data(response)
        countries_urls = req_country_json_content["shippingOptionsInfo"]["requestedShippingCountryBusinessUnits"]
        for country_data in countries_urls:
            brand_name = country_data["brandName"]
            if brand_name == "Gap":
                base_url = country_data["businessUnitUrl"]
                item["new_base_Url"] = base_url
                item["brand_Name"] = brand_name
                yield scrapy.Request(url=base_url,
                                     dont_filter=True, meta={"item": item}, callback=self.parse_new_homepage)

    def parse_new_homepage(self, response):
        item = response.meta["item"]
        categories_links = response.xpath('.//li[@class="topNavItem"]//a/@href').extract()
        for category in categories_links:
            category_url = response.url + category
            yield scrapy.Request(url=category_url,
                                 dont_filter=True, meta={"item": item}, callback=self.parse_categories_page)

    def parse_categories_page(self, response):
        item = response.meta["item"]
        base_url = item["new_base_Url"]
        sub_category_links = response.xpath('.//a[@class="sidebar-navigation--category--link"]/@href').extract()
        for product_page_url in sub_category_links:
            data_contains_id = re.search('(\d+)$', product_page_url)
            final_id = data_contains_id.group()
            req_country_url = base_url + '/resources/productSearch/v1/search?cid=' + final_id
            item["refer_url"] = req_country_url
            item["timestamp"] = time.asctime(time.localtime(time.time()))
            yield scrapy.Request(url=req_country_url,
                                 dont_filter=True, meta={"item": item}, callback=self.parse_each_page)

    def parse_each_page(self, response):
        item = response.meta["item"]
        base_url = item["new_base_Url"]
        product_urls = []
        data_having_product_ids = json.loads(response.body)
        p_cid = data_having_product_ids["productCategoryFacetedSearch"]["productCategory"]["businessCatalogItemId"]
        data_contains_c_id = data_having_product_ids["productCategoryFacetedSearch"]["productCategory"].get(
            "childCategories")
        if data_contains_c_id is not None:
            for i in data_contains_c_id:
                if isinstance(i, dict):
                    c_id = i.get("businessCatalogItemId")
                    if c_id is not None:
                        data_having_p_id = i.get("childProducts")
                        for j in data_having_p_id:
                            if isinstance(j, dict):
                                p_id = j.get("businessCatalogItemId")
                                product_urls.append('/browse/product.do?cid={}&pcid={}&pid={}'.format
                                                    (c_id, p_cid, p_id))
                    else:
                        data_having_p_id = i.get("childProducts")
                        for j in data_having_p_id:
                            if isinstance(j, dict):
                                p_id = j.get("businessCatalogItemId")
                                product_urls.append('/browse/product.do?pcid={}&pid={}'.format(p_cid, p_id))
        for url in product_urls:
            yield scrapy.Request(url=base_url+url, meta={"items": item}, dont_filter=True, callback=self.parse_data)

    def get_description(self, response):
        product_details = response.xpath(
            './/ul[@class="sp_top_sm dash-list"]//li[@class="dash-list--item"]/text()').extract()
        fabric_care = response.xpath('.//div[@class="sp_top_sm"]//p/text()').extract()
        return product_details+fabric_care

    def json_content(self, response):
        data_in_unicode = response.xpath('//script[contains(text(),"bvConversationApiUrl")]/text()').extract_first()
        if isinstance(data_in_unicode, unicode):
            data_in_str = data_in_unicode.encode("utf8")
            json_data = re.search('({.+})', data_in_str)
            final_data = json_data.group()
            product_json_content = json.loads(final_data)
            return product_json_content

    def get_title(self, response):
        product_json_content = self.json_content(response)
        return product_json_content["name"]

    def get_image_url(self, response):
        product_json_content = self.json_content(response)
        return product_json_content.get("currentColorMainImage")

    def get_new_price(self, response):
        product_json_content = self.json_content(response)
        return product_json_content["currentMinPrice"]

    def get_old_price(self, response):
        product_json_content = self.json_content(response)
        return product_json_content["regularMinPrice"]

    def color_and_sizes(self, response):
        product_json_content = self.json_content(response)
        color_details = product_json_content["variants"][0]
        size_details = color_details["productStyleColors"]
        available_sizes_and_colors = []
        for i in size_details:
            for j in i:
                color_information = {}
                color_information["color"] = {}
                color_code = j.get("businessCatalogItemId")
                color_name = j.get("colorName")
                color_information["color"]["color_code"] = color_code
                color_information["color"]["color_name"] = color_name
                list_having_size_info = []
                sizes_content = j.get("sizes")
                for sizes_info in sizes_content:
                    final_sizes_data = {}
                    final_sizes_data["size_identifier"] = sizes_info.get('skuId')
                    final_sizes_data["size"] = sizes_info.get("sizeDimension1")
                    stock = sizes_info.get('inStock')
                    if int(stock):
                        final_sizes_data["stock"] = 1
                    else:
                        final_sizes_data["stock"] = 0
                    list_having_size_info.append(final_sizes_data)
                color_information["color"]["size_info"] = list_having_size_info
                available_sizes_and_colors.append(color_information)
        return available_sizes_and_colors

    def parse_data(self, response):
        item = response.meta["items"]
        item["url"] = response.url
        base_url = item["new_base_Url"]
        item["description"] = self.get_description(response)
        item["image_url"] = base_url+self.get_image_url(response)
        item["title"] = self.get_title(response)
        item["new_price_text"] = self.get_new_price(response)
        item["old_price_text"] = self.get_old_price(response)
        item["color"] = self.color_and_sizes(response)
        yield item