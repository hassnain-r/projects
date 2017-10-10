from __future__ import absolute_import
import scrapy
from daraz.items import DarazItem


class DarazPakistan(scrapy.Spider):
    name = 'daraz_items_extractor'
    start_urls = ['https://www.daraz.pk/']
    list_having_next_pages_urls = []

    def parse(self, response):
	item = DarazItem()
	list_of_categories = response.xpath('.//ul[@class="menu-items"]//span[@class="nav-subTxt"]/text()').extract()
	item['All_categories'] = list_of_categories
	yield item
	list_having_sub_categories = response.xpath('.//ul[@class="menu-items"]//a/@href').extract()
	for sub_category in list_having_sub_categories:
	    yield scrapy.FormRequest(url=sub_category, method='GET', meta={'dont_merge_cookies': True},
		                     dont_filter=True, callback=self.parse_next_pages)
    
    def parse_next_pages(self, response):
        next_page_url = response.xpath('.//a[@title="Next"]/@href').extract_first()
        if next_page_url:
            self.list_having_next_pages_urls.append(next_page_url)
            yield scrapy.Request(url=next_page_url, method='GET', meta={'dont_merge_cookies': True},
                                 callback=self.parse_next_pages)
        else:
            list_of_next_page_urls = self.list_having_next_pages_urls
            for each_url in list_of_next_page_urls:
                yield scrapy.Request(url=each_url, dont_filter=True, method='GET', meta={'dont_merge_cookies': True},
                                     callback=self.parse_product_details)

    def parse_product_details(self, response):
        list_having_urls = response.xpath('.//section[@class="products"]//a[@class="link"]/@href').extract()
        for each_url in list_having_urls:
            yield scrapy.Request(url=each_url, method='GET', meta={'dont_merge_cookies': True},
                                 callback=self.parse_final_page)

    def parse_final_page(self, response):
        item = DarazItem()
        final_price = response.xpath('.//span[@class="price"]/span/text()').extract()
        if final_price:
            price = ''.join(final_price)
            price = price.replace(u'\xa0', u'')
            item['final_price'] = price
        else:
            final_price = response.xpath('.//span[@class="price -no-special"]/span/text()').extract()
            price = ''.join(final_price)
            price = price.replace(u'\xa0', u'')
            item['final_price'] = price
        old_price = response.xpath('.//span[@class="price -old"]/span/text()').extract()
        if old_price:
            price = ''.join(old_price)
            price = price.replace(u'\xa0', u'')
            item['old_price'] = price

        item['key_features'] = response.xpath('.//div[@class="list -features"]//li/text()').extract()
        item['description'] = response.xpath('.//h1[@class="title"]/text()').extract_first()
        item['delivery_info'] = response.xpath('.//div[@class="description"]/span[@class="title"]/text()').extract()
        item['brand_name'] = response.xpath('.//h1[@class="title"]/text()').extract_first()
        item['image_urls'] = response.xpath('.//div[@id="thumbs-slide"]/a/@href').extract()
        item['path_leads_to_product'] = response.xpath('.//nav[@class="osh-breadcrumb"]//a/text()').extract()
        item['percentage_discount'] = response.xpath('.//span[@class="sale-flag-percent"]/text()').extract_first()
        item['available_sizes'] = response.xpath(
            './/div[@class="list -sizes"]//span[@class="sku-size -available"]/text()').extract()
        yield item

