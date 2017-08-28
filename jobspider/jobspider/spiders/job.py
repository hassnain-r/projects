# code that scraped a simple website


 
import scrapy


class JobsSite(scrapy.Spider):
    name = 'jobdetails'
    start_urls = ['https://jobs.aapt.org/jobs?gclid=EAIaIQobChMIx_e-6_jg1QIVVjPTCh3UNQpWEAAYASAAEgIG-fD_BwE']

    def parse(self, response):
        for s in response.xpath('.//div[@class="bti-ui-job-detail-container"]'):
            yield {
                'job title': s.xpath('.//a[@id="jobURL"]/text()').extract_first(),
                'posting date': s.xpath('.//div[@class="bti-ui-job-result-detail-age"]/text()').extract_first(),
                'country location': s.xpath(
                    './/div[@class="bti-ui-job-result-detail-location"]/text()').extract_first(),
                'institute name': s.xpath('.//div[@class="bti-ui-job-result-detail-employer"]/text()').extract_first(),
            }
        for href in response.xpath('.//div/a[@class="bti-pagination-page-link"]/@href'):
            yield response.follow(href, callback=self.parse)
