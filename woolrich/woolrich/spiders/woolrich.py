from __future__ import absolute_import
import scrapy
import time
import urlparse
from woolrich.items import WoolrichItem


class WoolRich(scrapy.Spider):
    name = "wool_rich_crawler"
    start_urls = ["http://www.woolrich.com/woolrich/"]
    post_req_url = "http://www.woolrich.com/woolrich/prod/fragments/productDetails.jsp"
    product_urls = []

    def parse(self, response):
        categories = response.xpath('.//div[@class="menu-bar"]//a/@href').extract()
        for category in categories:
            category_url = urlparse.urljoin(response.url, category)
            yield scrapy.Request(url=category_url, callback=self.parse_next_pages)

    def parse_next_pages(self, response):
        products = response.xpath('.//h2//a[@title="View Details"]/@href').extract()
        for product in products:
            product_url = urlparse.urljoin(response.url, product)
            self.product_urls.append(product_url)
        next_page = response.xpath('.//div[@class="clear addMore"]/@nextpage').extract_first()
        if next_page:
            next_page_url = urlparse.urljoin(response.url, next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse_next_pages)
        else:
            for url in self.product_urls:
                yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_product)

    def get_image_urls(self, response):
        images_url = []
        images_data = response.xpath('.//ul[@class="colorlist"]//a//img/@src').extract()
        for image in images_data:
            url = image.replace('swatch', 'large')
            url = url.replace("version=1", "")
            images_url.append(url)
        return images_url

    def get_title(self, response):
        title = response.xpath('.//div[@class="pdp_title"]//h1/text()').extract_first()
        return title

    def brand_name(self, response):
        return "Woolrich"

    def get_description(self, response):
        description = response.xpath('.//span[@itemprop="description"]/text()').extract()
        return description

    def get_care(self, response):
        return response.xpath('.//div[@class="text"]//li/text()').extract()

    def get_category(self, response):
        return response.xpath('.//div[@class="wrap breadcrumb"]//a/text()').extract()[1:]

    def get_time(self, respone):
        return time.asctime(time.localtime(time.time()))

    def currency(self, response):
        return "PKR"

    def parse_product(self, response):
        color_requests = []
        item = WoolrichItem()
        item["url_original"] = response.url
        item["url"] = response.url+"?countryCode=PK"
        item["image_urls"] = self.get_image_urls(response)
        item["title"] = self.get_title(response)
        item["brand_name"] = self.brand_name(response)
        item["description"] = self.get_description(response)
        item["care"] = self.get_care(response)
        item["category"] = self.get_category(response)
        item["timestamp"] = self.get_time(response)
        item["Currency"] = self.currency(response)
        product_id = response.xpath('.//span[@itemprop="productID"]/text()').extract_first()
        color_ids = response.xpath('.//ul[@class="colorlist"]//a//img/@colorid').extract()
        color_names = response.xpath('.//ul[@class="colorlist"]//a/@title').extract()
        for c_id, name in zip(color_ids, color_names):
            form_data = {
                'productId': product_id,
                'colorId': c_id,
                'colorDisplayName': name,
            }
            request = scrapy.FormRequest(url=self.post_req_url, formdata=form_data, meta={'form_data': form_data, "item": item},
                                         dont_filter=True, callback=self.parse_color)
            color_requests.append(request)
        item["requests"] = color_requests
        return self.request_or_item(item)

    def parse_color(self, response):
        size_requests = []
        item = response.meta["item"]
        form_data = response.meta["form_data"]
        sizes = response.xpath('.//ul[@class="sizelist"]//a[@stocklevel!="0"]/@title').extract()
        sku_ids = response.xpath('.//ul[@class="sizelist"]//a[@stocklevel!="0"]/@id').extract()
        for size, s_id in zip(sizes, sku_ids):
            form_data["selectedSize"] = size
            form_data["skuId"] = s_id
            request = scrapy.FormRequest(url=self.post_req_url, formdata=form_data, meta={'form_data': form_data, "item": item},
                                         dont_filter=True, callback=self.parse_sizes)
            size_requests.append(request)
        item["requests"] += size_requests
        return self.request_or_item(item)

    def parse_sizes(self, response):
        dimension_request = []
        form_data = response.meta["form_data"]
        item = response.meta["item"]
        is_fit_exist = response.css('.dimensionslist').extract()
        if is_fit_exist:
            available_fits = response.xpath('.//ul[@class="dimensionslist"]//a[@stocklevel!="0"]/@title').extract()
            sku_ids = response.xpath('.//ul[@class="dimensionslist"]//a[@stocklevel!="0"]/@id').extract()
            for fit, s_id in zip(available_fits, sku_ids):
                form_data["skuId"] = s_id
                form_data["selectedDimension"] = fit
                request = scrapy.FormRequest(url=self.post_req_url, formdata=form_data,
                                             meta={'form_data': form_data, "item": item},
                                             dont_filter=True,  callback=self.parse_dimension_data)
                dimension_request.append(request)
            item["requests"] += dimension_request
            return self.request_or_item(item)
        else:
            skus = self.get_sku(response)
            item["skus"] = skus
            return self.request_or_item(item)

    def get_color(self, response):
        color = response.xpath('.//span[@class="colorName"]/text()').extract_first()
        f_color = color.replace(u"\xa0", u"")
        return f_color

    def get_price(self, response):
        price = response.xpath('.//span[@itemprop="price"]/@content').extract_first()
        return price.split()

    def get_size(self, response):
        size = response.css('.sizelist .selected ::text').extract_first()
        return size

    def get_currency(self, response):
        currency = response.xpath('.//span[@itemprop="priceCurrency"]/text()').extract_first()
        return currency

    def get_old_price(self, response):
        old_price = response.xpath('.//span[@class="price_reg strikethrough"]/text()').extract_first()
        if old_price:
            return old_price.split()

    def get_sku(self, response):
        item = response.meta["item"]
        skus = item.setdefault('skus', {})
        sku_id = response.css('.sizelist .selected ::attr("id")').extract_first()
        skus[sku_id] = {}
        skus[sku_id]["size"] = self.get_size(response)
        skus[sku_id]["color"] = self.get_color(response)
        skus[sku_id]["price"] = self.get_price(response)
        skus[sku_id]["currency"] = self.get_currency(response)
        skus[sku_id]["old_price"] = self.get_old_price(response)
        return skus

    def parse_dimension_data(self, response):
        item = response.meta["item"]
        dim_sku_id = response.css('.dimensionslist .selected ::attr("id")').extract_first()
        skus = item.setdefault('skus', {})
        skus[dim_sku_id] = {}
        skus[dim_sku_id]["color"] = self.get_color(response)
        skus[dim_sku_id]["price"] = self.get_price(response)
        skus[dim_sku_id]["currency"] = self.get_currency(response)
        skus[dim_sku_id]["old_price"] = self.get_old_price(response)
        dimension = response.css('.dimensionslist .selected ::text').extract_first()
        size = self.get_size(response)
        split_dimension = dimension.split()
        if isinstance(split_dimension, list):
            product_dim = ''.join(split_dimension)
            skus[dim_sku_id]["size"] = size + "/" + product_dim
            return self.request_or_item(item)

    def request_or_item(self, item):
        if item["requests"]:
            return item["requests"].pop()
        else:
            del item['requests']
            return item
