from __future__ import absolute_import
import scrapy
from dockets.items import DocketsItem


class Dockets(scrapy.Spider):
    name = 'cpcu_docs'
    start_urls = ['http://docs.cpuc.ca.gov/advancedsearchform.aspx']
    data_having_docIds = []
    dockets_ids = []
    dockets_ids_index = 0
    search_formdata = {}

    def parse(self, response):
        selector = response.xpath('//html/*/form[@id="frmSearchForm"]')
        form_data = {
            '__VIEWSTATE': selector.xpath('.//input[@id="__VIEWSTATE"]/@value').extract_first(),
            '__VIEWSTATEGENERATOR': selector.xpath('.//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(),
            '__EVENTVALIDATION': selector.xpath('.//input[@id="__EVENTVALIDATION"]/@value').extract_first(),
            'FilingDateFrom': '09/18/17',
            'FilingDateTo': '09/19/17',
            'SearchButton': 'Search'
        }
        self.search_formdata = form_data
        yield scrapy.FormRequest('http://docs.cpuc.ca.gov/SearchRes.aspx',
                                 formdata=form_data, dont_filter=True, callback=self.parse_pagination)

    def parse_pagination(self, response):
        previous_form_data = self.search_formdata
        selector = response.xpath('//html/*/form[@id="frmResultList"]')
        eventtarget_value = selector.xpath('.//td/a[@id="lnkNextPage"]/@id').extract_first()
        if eventtarget_value:
            formdata = {
                '__EVENTTARGET': eventtarget_value,
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': selector.xpath('.//input[@id="__VIEWSTATE"]/@value').extract_first(),
                '__VIEWSTATEGENERATOR': selector.xpath('.//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(),
                '__EVENTVALIDATION': selector.xpath('.//input[@id="__EVENTVALIDATION"]/@value').extract_first(),
            }
            data = selector.xpath('.//tr/td[@class="ResultTitleTD"]/text()').extract()
            self.data_having_docIds.append(data)
            yield scrapy.FormRequest('http://docs.cpuc.ca.gov/SearchRes.aspx', formdata=formdata,
                                     meta={"form_data": previous_form_data}, callback=self.parse_pagination)
        else:
            yield scrapy.FormRequest('http://docs.cpuc.ca.gov/SearchRes.aspx', dont_filter=True,
                                     callback=self.parse_list)

    def parse_list(self, response):
        data_in_multiplelists = self.data_having_docIds
        list_having_data = sum(data_in_multiplelists, [])  # combining sub lists to make a single list
        size_of_list = len(list_having_data)
        selected_data = []
        dockets_data = []
        starting_index = 1
        while starting_index < size_of_list:  # looping throug a list that contain docket_ids at odd indexes only i.e (1,3,5,7,.....)
            selected_data.append(list_having_data[starting_index])
            starting_index = starting_index + 2
        for i in selected_data:
            ids_str = ''
            is_present = 0
            for j in i:
                if j == ':':
                    is_present = 1
                elif is_present == 1:
                    ids_str += j
            spliting_string = ids_str.split(';')
            dockets_data += spliting_string
        for dockets_id in dockets_data:
            final_docketid = dockets_id.replace(' ', '')
            self.dockets_ids.append(final_docketid)
        starting_link = 'https://apps.cpuc.ca.gov/apex/f?p=401:56:5943774781817::NO:RP,57,RIR:P5_PROCEEDING_SELECT:' + \
                        self.dockets_ids[self.dockets_ids_index]
        yield scrapy.Request(starting_link, dont_filter=True, method='GET', callback=self.parse_data)

    def parse_data(self, response):  # extracting required data from procceding page
        item = DocketsItem()

        item['description'] = response.xpath('.//span[@id="P56_DESCRIPTION"]/text()').extract()
        item['assinges'] = response.xpath('.//span[@id="P56_STAFF"]/text()').extract()
        item['filled_by'] = response.xpath('.//span[@id="P56_FILED_BY"]/text()').extract()
        yield item

        formdata = {
            'p_flow_id': response.xpath('.//input[@name="p_flow_id"]/@value').extract_first(),
            'p_flow_step_id': response.xpath('.//input[@name="p_flow_step_id"]/@value').extract_first(),
            'p_instance': response.xpath('.//input[@name="p_instance"]/@value').extract_first(),
            'p_page_submission_id': response.xpath('.//input[@name="p_page_submission_id"]/@value').extract_first(),
            'p_request': 'T_DOCUMENTS',
            'p_page_checksum': response.xpath('.//input[@name="p_page_checksum"]/@value').extract_first(),
            'p_md5_checksum': response.xpath('.//input[@name="p_md5_checksum"]/@value').extract_first(),
        }

        yield scrapy.FormRequest('https://apps.cpuc.ca.gov/apex/f?p=401:57:0::NO',
                                 dont_filter=True, formdata=formdata, callback=self.parse_page)

    def parse_page(self, response):  # from procceding page it moves to document page and extract more data
        item = DocketsItem()
        item["filling_date"] = response.xpath('//tr/td[@headers="FILING_DATE"]/text()').extract_first()
        item["filled__by"] = response.xpath('//td[@headers="FILED_BY"]/text()').extract_first()
        yield item
        list_having_links = response.xpath('//td[@headers="DOCUMENT_TYPE"]//a/@href').extract()
        starting_link = ''
        if len(list_having_links) > 0:
            starting_link = list_having_links[0]
        yield scrapy.Request(starting_link, method="GET", dont_filter=True, callback=self.parse_endpage,
                             meta={"list_having_links": list_having_links, 'index': 0, 'dont_merge_cookies': True})

    def parse_endpage(self, response):  # move to the last page and extract data
        item = DocketsItem()
        selector = response.xpath('//html/*/form[@id="frmResultList"]')
        data_contains_title = selector.xpath('//td[@class="ResultTitleTD"]/text()').extract()
        size_of_list = len(data_contains_title)
        title = []
        index1 = 0
        while index1 < size_of_list:  # looping through a list that contain title_line at even indexes only i.e (0,2,4,6,......)
            title.append(data_contains_title[index1])
            index1 += 2
        source_url = response.xpath('//td[@class="ResultLinkTD"]/a/@href').extract()
        extension = selector.xpath('//td[@class="ResultLinkTD"]/a/text()').extract()
        for t, e, s_url in zip(title, extension, source_url):
            item['title'] = t
            item['extension'] = e
            item['source_url'] = s_url
            yield item
        list_having_links = response.meta["list_having_links"]
        index = response.meta['index'] + 1
        if len(list_having_links) > index:
            starting_link = list_having_links[index]
        else:
            self.dockets_ids_index += 1
            link_str = 'https://apps.cpuc.ca.gov/apex/f?p=401:56:5943774781817::NO:RP,57,RIR:P5_PROCEEDING_SELECT:'
            starting_link = link_str + self.dockets_ids[self.dockets_ids_index]
            yield scrapy.Request(starting_link, dont_filter=True, method='GET', callback=self.parse_data)
            return
        yield scrapy.Request(starting_link, meta={"list_having_links": list_having_links, 'index': index,
                                    'dont_merge_cookies': True},dont_filter=True, callback=self.parse_endpage)