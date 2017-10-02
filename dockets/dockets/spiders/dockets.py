import re
import scrapy
from compiler.ast import flatten


class Dockets(scrapy.Spider):
    name = 'cpcu_docs'
    searched_url = 'http://docs.cpuc.ca.gov/advancedsearchform.aspx'
    start_urls = [searched_url]

    def parse(self, response):
        selector = response.xpath('//html/*/form[@id="frmSearchForm"]')
        form_data = {
            '__VIEWSTATE': selector.xpath('.//input[@id="__VIEWSTATE"]/@value').extract_first(),
            '__VIEWSTATEGENERATOR': selector.xpath('.//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(),
            '__EVENTVALIDATION': selector.xpath('.//input[@id="__EVENTVALIDATION"]/@value').extract_first(),
            'FilingDateFrom': '09/15/17',
            'FilingDateTo': '09/19/17',
            'SearchButton': 'Search'
        }

        yield scrapy.FormRequest('http://docs.cpuc.ca.gov/SearchRes.aspx', formdata=form_data, dont_filter=True,
                                 meta={"key_list": [], "form_data": form_data}, callback=self.parse_pagination)

    def parse_pagination(self, response):
        selector = response.xpath('//html/*/form[@id="frmResultList"]')
        key_list = response.meta["key_list"]
        pre_call_data = response.meta["form_data"]
        a = selector.xpath('.//td/a[@id="lnkNextPage"]/@id').extract_first()
        if a:
            data2 = {
                '__EVENTTARGET': a,
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': selector.xpath('.//input[@id="__VIEWSTATE"]/@value').extract_first(),
                '__VIEWSTATEGENERATOR': selector.xpath('.//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(),
                '__EVENTVALIDATION': selector.xpath('.//input[@id="__EVENTVALIDATION"]/@value').extract_first(),
            }
            key_word = selector.xpath('.//tr/td[@class="ResultTitleTD"]/text()').extract()
            key_list += key_word
            yield scrapy.FormRequest('http://docs.cpuc.ca.gov/SearchRes.aspx',
                                     meta={"key_list": key_list, "form_data": pre_call_data}, formdata=data2,
                                     callback=self.parse_pagination)
        else:
            yield scrapy.FormRequest('http://docs.cpuc.ca.gov/SearchRes.aspx', dont_filter=True, formdata=pre_call_data,
                                     meta={"key_list": key_list}, callback=self.parse_list)

    def parse_list(self, response):
        list_of_links = response.meta["key_list"]
        length = len(list_of_links)
        final_list = []
        result = []
        dockets_ids = []
        i = 1
        while i <= length:
            final_list.append(list_of_links[i])
            i = i + 2
        for i in final_list:
            ids_str = ''
            bol_is_present = 0
            for j in i:
                if j == ':':
                    bol_is_present = 1
                elif bol_is_present == 1:
                    ids_str += j
            s = ids_str.split(';')
            result += s
        for value in result:
            exact_value = value.replace(' ', '')
            dockets_ids.append(exact_value)
        new_link = 'https://apps.cpuc.ca.gov/apex/f?p=401:56:5943774781817::NO:RP,57,RIR:P5_PROCEEDING_SELECT:' + \
                   dockets_ids[0]
        yield scrapy.Request(new_link, method='GET', callback=self.parse_data,
                             meta={"dids": dockets_ids, 'index': 0})

    def parse_data(self, response):
        print ({
            'description': response.xpath('.//span[@id="P56_DESCRIPTION"]/text()').extract_first(),
            'assignes': response.xpath('.//span[@id="P56_STAFF"]/text()').extract(),
            'filled_by': response.xpath('.//span[@id="P56_FILED_BY"]/text()').extract(),
        })
        data1 = {
            'p_flow_id': response.xpath('.//input[@name="p_flow_id"]/@value').extract_first(),
            'p_flow_step_id': response.xpath('.//input[@name="p_flow_step_id"]/@value').extract_first(),
            'p_instance': response.xpath('.//input[@name="p_instance"]/@value').extract_first(),
            'p_page_submission_id': response.xpath('.//input[@name="p_page_submission_id"]/@value').extract_first(),
            'p_request': 'T_DOCUMENTS',
            'p_page_checksum': response.xpath('.//input[@name="p_page_checksum"]/@value').extract_first(),
            'p_md5_checksum': response.xpath('.//input[@name="p_md5_checksum"]/@value').extract_first(),
        }
        dids = response.meta["dids"]
        index = response.meta['index'] + 1
        try:
            new_link = 'https://apps.cpuc.ca.gov/apex/f?p=401:56:5943774781817::NO:RP,57,RIR:P5_PROCEEDING_SELECT:' + \
                       dids[index]
            yield scrapy.Request(new_link, meta={"dids": dids, 'index': index}, callback=self.parse_data,
                                 dont_filter=True)
            yield scrapy.FormRequest.from_response(response, dont_filter=True, formdata=data1,
                                                   callback=self.parse_page)
        except:
            return

    def parse_page(self, response):
        yield {
            'filling_date': response.xpath('//tr/td[@headers="FILING_DATE"]/text()').extract_first(),
            'filled_by': response.xpath('//td[@headers="FILED_BY"]/text()').extract_first(),
        }
        data4 = response.xpath('//td[@headers="DOCUMENT_TYPE"]//a/@href').extract()
        first_link = data4[0]
        yield scrapy.Request(first_link, method="GET", dont_filter=True, callback=self.parse_ending,
                             meta={"data4": data4, 'index1': 0})

    def parse_endpage(self, response):
        data4 = response.meta["data4"]
        index1 = response.meta['index1'] + 1
        list_of_title = response.xpath('//td[@class="ResultTitleTD"]/text()').extract()
        size = len(list_of_title)
        title = []
        i = 0
        while i < size:
            title.append(list_of_title[i])
            i += 2
        s_url = response.xpath('//td[@class="ResultLinkTD"]/a/@href').extract()
        extenshion = response.xpath('//td[@class="ResultLinkTD"]/a/text()').extract()
        for t, e, s_ur in zip(title, extenshion, s_url):
            yield {
                'title': t,
                'extension': e,
                'sourse_url': s_ur,
            }
        try:
            first_link = data4[index1]
            yield scrapy.Request(first_link, meta={"data4": data4, 'index1': index1}, callback=self.parse_endpage,                                 dont_filter=True)
        except:
            return