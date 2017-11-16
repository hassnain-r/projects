from __future__ import absolute_import
import scrapy
import json
import time
from gap.items import GapItem


class GapProducts(scrapy.Spider):
    name = "gap.com_extractor"
    start_urls = ["http://www.gap.com/"]

    def parse(self, response):
        user_input_countries = raw_input("Enter Country Codes in a list: ")
        list_of_countries = json.loads(user_input_countries)
        for each_country in list_of_countries:
            requested_country_url = "https://secure-www.gap.com/resources/shippingOptions/v1/"+each_country
            yield scrapy.Request(url=requested_country_url, dont_filter=True, callback=self.parse_new_base_url)

    def parse_new_base_url(self, response):
        item = GapItem()
        req_country_json_content = json.loads(response.body)
        item["country_code"] = req_country_json_content["shippingOptionsInfo"]["requestedShippingCountryCode"]
        item["currency"] =\
            req_country_json_content["shippingOptionsInfo"]["availableGlobalShippingCountryCurrency"]["currencyName"]
        countries_urls = req_country_json_content["shippingOptionsInfo"]["requestedShippingCountryBusinessUnits"]
        for each_country_data in countries_urls:
            brand_name = each_country_data["brandName"]
            if brand_name == "Gap":
                base_url = each_country_data["businessUnitUrl"]
                item["new_base_Url"] = base_url
                item["brand_Name"] = brand_name
                yield scrapy.Request(url=base_url,
                                     dont_filter=True, meta={"item": item}, callback=self.parse_new_homepage)

    def parse_new_homepage(self, response):
        item = response.meta["item"]
        categories_links = response.xpath('.//li[@class="topNavItem"]//a/@href').extract()
        for each_category in categories_links:
            category_url = response.url+each_category
            yield scrapy.Request(url=category_url,
                                 dont_filter=True, meta={"item": item}, callback=self.parse_categories_page)

    def parse_categories_page(self, response):
        item = response.meta["item"]
        base_url = item["new_base_Url"]
        sub_category_link = response.xpath('.//a[@class="sidebar-navigation--category--link"]/@href').extract()
        for product_page_urls in sub_category_link:
            data_contains_id = base_url + product_page_urls
            starting_point = data_contains_id.find("=") + 1
            final_char = data_contains_id[len(data_contains_id) - 1]
            ending_point = data_contains_id.find(final_char, starting_point)
            final_id = data_contains_id[starting_point:ending_point + 6]
            new_request_page = '/resources/productSearch/v1/search?cid='
            link_contain_req_json_content = new_request_page.replace("=", "=" + final_id)
            req_country_url = base_url+link_contain_req_json_content
            item["refer_url"] = req_country_url
            item["timestamp"] = time.asctime(time.localtime(time.time()))
            yield scrapy.Request(url=req_country_url,
                                 dont_filter=True, meta={"item": item}, callback=self.parse_each_page)

    def parse_each_page(self, response):
        item = response.meta["item"]
        base_url = item["new_base_Url"]
        list_having_product_urls = []
        data_having_product_ids = json.loads(response.body)
        p_cid = data_having_product_ids["productCategoryFacetedSearch"]["productCategory"]["businessCatalogItemId"]
        c_id_data = data_having_product_ids["productCategoryFacetedSearch"]["productCategory"].get("childCategories")
        if c_id_data is not None:
            for i in c_id_data:
                c_id = i.get("businessCatalogItemId")
                p_id_data = i.get("childProducts")
                for j in p_id_data:
                    if isinstance(j, dict):
                        p_id = j.get("businessCatalogItemId")
                        list_having_product_urls.append('/browse/product.do?cid={}&pcid={}&pid={}'.
                                                        format(c_id, p_cid, p_id))
        for each_url in list_having_product_urls:
            each_product_url = base_url+each_url
            item["url"] = each_product_url
            yield scrapy.Request(url=each_product_url, meta={"items": item}, dont_filter=True, callback=self.parse_data)

    def parse_data(self, response):
        item = response.meta["items"]
        base_url = item["new_base_Url"]
        product_details = response.xpath(
            './/ul[@class="sp_top_sm dash-list"]//li[@class="dash-list--item"]/text()').extract()
        fab_care = response.xpath('.//div[@class="sp_top_sm"]//p/text()').extract()
        item["description"] = product_details + fab_care
        data_in_unicode = response.xpath('//script[contains(text(),"bvConversationApiUrl")]/text()').extract_first()
        data_in_str = data_in_unicode.encode("utf8")
        start = data_in_str.find('= {') + 1
        end = data_in_str.find('};', start)
        final = data_in_str[start:end + 1]
        product_json_content = json.loads(final)
        min_price = product_json_content["currentMinPrice"]
        max_price = product_json_content["regularMinPrice"]
        item["image_url"] = base_url + product_json_content["currentColorMainImage"]
        item["new_price_text"] = min_price
        item["old_price_text"] = max_price
        item["title"] = product_json_content["name"]
        color_details = product_json_content["variants"][0]
        size_details = color_details["productStyleColors"]
        available_sizes_and_colors = []
        for i in size_details:
            for j in i:
                dict_having_colors_info = {}
                dict_having_colors_info["color"] = {}
                color_code = j.get("businessCatalogItemId")
                color_name = j.get("colorName")
                dict_having_colors_info["color"]["color_code"] = color_code
                dict_having_colors_info["color"]["color_name"] = color_name
                list_having_size_info = []
                sizes_content = j.get("sizes")
                for sizes_info in sizes_content:
                    final_sizes_data = {}
                    final_sizes_data["size_identifier"] = sizes_info.get('skuId')
                    final_sizes_data["size"] = sizes_info.get("sizeDimension1")
                    stock = sizes_info.get('inStock')
                    if stock is True:
                        final_sizes_data["stock"] = 1
                    else:
                        final_sizes_data["stock"] = 0
                    list_having_size_info.append(final_sizes_data)
                dict_having_colors_info["color"]["size_info"] = list_having_size_info
                available_sizes_and_colors.append(dict_having_colors_info)
        item["color"] = available_sizes_and_colors
        yield item
