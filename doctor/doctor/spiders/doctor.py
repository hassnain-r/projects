import scrapy

class doc_items(scrapy.Item):
    crawled_date=scrapy.Field()
    specialty=scrapy.Field()
    sourse_url=scrapy.Field()
    affiliation=scrapy.Field()
    medical_school=scrapy.Field()
    image_url=scrapy.Field()
    full_name=scrapy.Field()
    address=scrapy.Field()
    graduate_education=scrapy.Field()




class doctor (scrapy.Spider):
    name='profile'
    searched_url='https://www.nwh.org/find-a-doctor/find-a-doctor-home?type=1'
    start_urls=[searched_url]

    def parse(self,response):

        search=response.xpath('.//a[@class="link-name-profile"]/@id').extract()

        for i in search:
            r=i.replace('_','$')

            data = {
                '__EVENTTARGET': r,
                '__VIEWSTATE': response.xpath('.//input[@id="__VIEWSTATE"]/@value').extract(),
                '__VIEWSTATEGENERATOR': response.xpath('.//input[@id="__VIEWSTATEGENERATOR"]/@value').extract(),

            }

            yield scrapy.FormRequest(url=self.searched_url, formdata=data, callback=self.parse_name)

    def parse_name(self, response):
        item=doc_items()
        item['specialty']=response.xpath('.//div[@class="pnl-doctor-specialty"]/h2/text()').extract_first()
        item['affiliation']=response.xpath('.//div[@class="panel-doc-qualification"]//li/text()').extract()[0]
        item['medical_school']=response.xpath('.//div[@class="panel-doc-qualification"]//li/text()').extract()[1]
        item['image_url']=response.xpath('.//meta[@name="og:image"]/@content').extract_first()
        item['full_name'] = response.xpath('.//div/h1[@class="header-doctor-name"]/text()').extract_first()
        item['address']=response.xpath('//div[@class="doctor-contact-location-address clearfix"]/a[@target="_blank"]/text()').extract()
        #if condition is required
        item['graduate_education']=response.xpath('.//div[@class="panel-doc-qualification"]//li/text()').extract()[3]

        yield item







