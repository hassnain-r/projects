import scrapy
from scrapy.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from datetime import datetime


class DocItems(scrapy.Item):
    crawled_date = scrapy.Field()
    source_url = scrapy.Field()
    address = scrapy.Field()
    speciality = scrapy.Field()
    affiliation = scrapy.Field()
    medical_school = scrapy.Field()
    graduate_education = scrapy.Field()
    full_name = scrapy.Field(output_processor=TakeFirst())
    image_url = scrapy.Field(output_processor=TakeFirst())


class MySpider(scrapy.Spider):

    name = 'Doctor'
    searched_url = 'https://www.nwh.org/find-a-doctor/find-a-doctor-home?type=1'
    start_urls = [searched_url]

    def parse(self, response):
        search = response.xpath('.//a[@class="link-name-profile"]/@id').extract()
        for i in search:
            r = i.replace('_', '$')
            data = {
                '__EVENTTARGET': r,
                '__VIEWSTATE': response.xpath('.//input[@id="__VIEWSTATE"]/@value').extract(),
                '__VIEWSTATEGENERATOR': response.xpath('.//input[@id="__VIEWSTATEGENERATOR"]/@value').extract(),
            }
            yield scrapy.FormRequest(url=self.searched_url, formdata=data, callback=self.parse_name)

        search2 = response.xpath('.//div[@class="doc-pages"]//a[@class="page-button"]/@id').extract()
        for pages in search2:
            desire_output = pages.replace('_', '$')
            data2 = {
                '__EVENTTARGET': desire_output,
                '__VIEWSTATE': response.xpath('.//input[@id="__VIEWSTATE"]/@value').extract(),
                '__VIEWSTATEGENERATOR': response.xpath(
                    './/input[@id="__VIEWSTATEGENERATOR"]/@value').extract(),
            }
            yield scrapy.FormRequest(url=self.searched_url, formdata=data2, callback=self.parse)

        search3 = response.xpath('.//div[@class="doc-pages"]//a[@class="btn-prev-next"]/@id').extract()
        for next_pages in search3:
            next_out = next_pages.replace('_', '$')
            data3 = {
                '__EVENTTARGET': next_out,
                '__VIEWSTATE': response.xpath('.//input[@id="__VIEWSTATE"]/@value').extract(),
                '__VIEWSTATEGENERATOR': response.xpath(
                    './/input[@id="__VIEWSTATEGENERATOR"]/@value').extract(),
            }
            yield scrapy.FormRequest(url=self.searched_url, formdata=data3, callback=self.parse)

    def parse_name(self, response):
        l = ItemLoader(item=DocItems(), response=response)
        living = response.xpath(
            '//div[@class="doctor-contact-location-address clearfix"]/a[@target="_blank"]/text()').extract()
        phone_no = response.xpath('.//div[@class="pnl-doctor-contact-phone"]//a/span/text()').extract_first()
        fax_no = response.xpath('.//div[@class="pnl-doctor-contact-fax"]//span[@id]/text()').extract_first()
        l.add_value('address', {'phone': phone_no, 'other': living, 'fax': fax_no})
        special = map(unicode.strip, response.xpath('.//div[@class="pnl-doctor-specialty"]/h2/text()').extract())
        l.add_value('speciality', {'name': special})
        affiliated_institute = response.xpath('.//div[@class="panel-doc-qualification"]//li/text()').extract()[0]
        l.add_value('affiliation', {'name': affiliated_institute})
        m_school = response.xpath('.//div[@class="panel-doc-qualification"]//li/text()').extract()[1]
        l.add_value('medical_school', {'name': m_school})
        r_name = response.xpath('.//div[@class="panel-doc-qualification"]//li/text()').extract()[3]
        residence = response.xpath('.//div[@class="panel-doc-qualification"]//h2/text()').extract()[3]
        try:
            l.add_value('graduate_education', {'type': residence, 'name': r_name})
        except IndexError:
            l.add_value('graduate_education', {'type': 'nothing', 'name': 'nothing'})
        l.add_xpath('full_name', './/div/h1[@class="header-doctor-name"]/text()')
        l.add_xpath('image_url', './/meta[@name="og:image"]/@content')
        l.add_value('crawled_date', str(datetime.now()))
        yield l.load_item()




