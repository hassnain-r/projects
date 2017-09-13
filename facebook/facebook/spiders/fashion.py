import scrapy
import urlparse
from scrapy.loader import ItemLoader


class FashionItems(scrapy.Item):
    output = scrapy.Field()
    skus = scrapy.Field()
    material_care = scrapy.Field()


class FashionSite(scrapy.Spider):
    name = 'mainpage'
    start_urls = ['https://www.sheego.de/']

    def parse(self, response):

        urls = response.xpath('.//a[@class="cj-mainnav__entry-title"]/@href').extract()
        for url in urls:
            yield response.follow(url, callback=self.parse)

        articles_links = response.xpath(
            './/section[@class="pl__list js-productList at-product-list"]//a[@class="product__top js-productlink text-link--inherit"]/@href').extract()
        for every_article in articles_links:
            link = urlparse.urljoin('https://www.sheego.de/', every_article)

            yield response.follow(link, callback=self.parse_data)

        next_page_link = response.xpath('.//div[@class="cj-paging"]//span[@class="paging__btn"]//a/@href').extract()
        for next_page_url in next_page_link:
            url_no = urlparse.urljoin('https://www.sheego.de', next_page_url)
            yield response.follow(url_no, callback=self.parse)

    def parse_data(self, response):

        load = ItemLoader(item=FashionItems(), response=response)
	category = response.xpath('.//a[@class="at-breadcrumb-item"]/span/text()').extract()[1:]
        load.add_value('category',category)
        url = response.url
        start = url.find('_') + 1
        end = url.find('.', start)
        pid = url[start:end]
        description = response.xpath(
            './/div[@class="p-details__main__box l-hidden-xs l-hidden-s l-hidden-sm l-mt-10 l-text-3"]//ul[@class="l-list l-list--nospace"]/li/text()').extract()
        image_urls = response.xpath('.//div[@class="p-details__image__thumb__container"]//a/@href').extract()
        url_list = ['https://{0}'.format(i) for i in image_urls]
        article_number = response.xpath('.//div[@class="l-mb-20"]/span[@class="l-regular"]/text()').extract_first()
        article_number = article_number.replace('\n', '')
        article_number = article_number.replace('  ', '')
        article_value = map(unicode.strip,response.xpath('.//div[@class="l-mb-20"]/span[@class="js-artNr at-dv-artNr"]/text()').extract())
        brand = map(unicode.strip, response.xpath('.//section[@class="p-details__brand at-brand"]//a/text()').extract())
        name = map(unicode.strip, response.xpath('.//div//h1[@class="l-regular l-text-1 at-name"]/text()').extract())
        load.add_value('output', {'name':name, 'Gender':'Women','pid':pid, 'description':description, article_number:article_value, 'brand':brand , 'url_orignal':url, 'image_urls':url_list})
        colors = response.xpath('.//span[@class ="colorspots__wrapper"]//span/@title').extract()
        before_price = response.xpath('.//section//span[@class ="product__price__wrong js-wrongprice at-wrongprice"]/text()').extract_first()
        if before_price:
            before_price = before_price.replace(u'\xa0\u20ac', u'')
        price = response.xpath('.//section[@class="p-details__price at-dv-price-box p-details__price--short"]//span/text()').extract_first()
        if price:
            price = price.replace(u'\xa0\u20ac    ', u'')
            price = price.replace(u'\n                 ', '')
        currency = response.xpath(
            './/div[@class="p-details__availability l-normal-lh"]//meta[@itemprop="priceCurrency"]/@content').extract_first()
        sizes = response.xpath('.//div[@class="l-hidden-xs l-hidden-s"]/div/text()').extract()
        for size in sizes:
            size = size.replace('\n    ', '')
            size = size.replace('\n', '')
            size_color = size + '_' + colors[0]
            load.add_value('skus', {size_color:{'available_colors':colors, 'size':size, 'before_price':before_price, 'price':price, 'currency':currency}})
        
	keys= map(unicode.strip, response.xpath('.//div[@class="f-xs-12 f-md-6"]//span[@class="p-details__material__desc"]/text()').extract())
        values = map(unicode.strip, response.xpath('.//div[@class="f-xs-12 f-md-6"]//td/text()').extract())
        final_list = []
        n = len(values)
        i = 2
        while i <= n:
            final_list.append(values[i])
            i = i + 3
        material_care = dict(zip(keys, final_list))
        load.add_value('material_care', material_care)
        yield  load.load_item()

