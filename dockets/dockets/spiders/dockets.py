from __future__ import absolute_import
import scrapy
from dockets.items import DocketsItem


class Dockets(scrapy.Spider):
    name = 'cpcu_docs_extractor'
    start_urls = ['http://docs.cpuc.ca.gov/advancedsearchform.aspx']
    list_of_data_having_docket_Ids = []
    list_of_docket_Ids = []
    docket_Ids_Index = 0
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
                                 formdata=form_data, dont_filter=True, callback=self.parse_next_pages)

    def parse_next_pages(self, response):
        previous_form_data = self.search_formdata
        selector = response.xpath('//html/*/form[@id="frmResultList"]')
        eventtarget = selector.xpath('.//td/a[@id="lnkNextPage"]/@id').extract_first()
        if eventtarget:
            formdata = {
                '__EVENTTARGET': eventtarget,
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': selector.xpath('.//input[@id="__VIEWSTATE"]/@value').extract_first(),
                '__VIEWSTATEGENERATOR': selector.xpath('.//input[@id="__VIEWSTATEGENERATOR"]/@value').extract_first(),
                '__EVENTVALIDATION': selector.xpath('.//input[@id="__EVENTVALIDATION"]/@value').extract_first(),
            }
            data = selector.xpath('.//tr/td[@class="ResultTitleTD"]/text()').extract()
            self.list_of_data_having_docket_Ids.append(data)
            yield scrapy.FormRequest('http://docs.cpuc.ca.gov/SearchRes.aspx', formdata=formdata,
                                     meta={"form_data": previous_form_data}, callback=self.parse_next_pages)
        else:
            yield scrapy.FormRequest('http://docs.cpuc.ca.gov/SearchRes.aspx', dont_filter=True,
                                     callback=self.parse_data_with_docket_ids)

    def parse_data_with_docket_ids(self, response):
        data_in_sub_lists = self.list_of_data_having_docket_Ids
        list_having_data = sum(data_in_sub_lists, [])  # combining sub lists to make a single list
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
            split_string = ids_str.split(';')
            dockets_data.append(split_string)
        for dockets_id in dockets_data:
            final_docket_id = dockets_id.replace(' ', '')
            self.list_of_docket_Ids.append(final_docket_id)
        starting_link = 'https://apps.cpuc.ca.gov/apex/f?p=401:56:5943774781817::NO:RP,57,RIR:P5_PROCEEDING_SELECT:' + \
                        self.list_of_docket_Ids[self.docket_Ids_Index]
        yield scrapy.Request(starting_link, dont_filter=True, method='GET', callback=self.parse_data)

    def parse_data(self, response):
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
                                 dont_filter=True, formdata=formdata, callback=self.parse_nextpage_data)

    def parse_nextpage_data(self, response):  
        item["filling_date"] = response.xpath('//tr/td[@headers="FILING_DATE"]/text()').extract_first()
        item["filled__by"] = response.xpath('//td[@headers="FILED_BY"]/text()').extract_first()
        yield item
        list_having_urls = response.xpath('//td[@headers="DOCUMENT_TYPE"]//a/@href').extract()
        starting_link = ''
        if len(list_having_urls) > 0:
            starting_link = list_having_urls[0]
        yield scrapy.Request(starting_link, method="GET", dont_filter=True, callback=self.parse_finalpage_data,
                             meta={"list_having_urls": list_having_urls, 'index': 0, 'dont_merge_cookies': True})

    def parse_finalpage_data(self, response):  # move to the last page and extract data
        selector = response.xpath('//html/*/form[@id="frmResultList"]')
        list_of_data_having_title = selector.xpath('//td[@class="ResultTitleTD"]/text()').extract()
        size_of_list = len(list_of_data_having_title)
        list_having_titles = []
        index1 = 0
        while index1 < size_of_list:  # looping through a list that contain title_line at even indexes only i.e (0,2,4,6,......)
            list_having_titles.append(list_of_data_having_title[index1])
            index1 += 2
        list_having_source_urls = response.xpath('//td[@class="ResultLinkTD"]/a/@href').extract()
        list_having_extensions = selector.xpath('//td[@class="ResultLinkTD"]/a/text()').extract()
        item = DocketsItem()
        for title, extension, source_url in zip(list_having_titles, list_having_extensions, list_having_source_urls):
            item['title'] = title
            item['extension'] = extension
            item['source_url'] = source_url
            yield item

        list_having_urls = response.meta["list_having_urls"]
        index = response.meta['index'] + 1
        if len(list_having_urls) > index:
            starting_link = list_having_urls[index]
        else:
            self.docket_Ids_Index += 1
            link_str = 'https://apps.cpuc.ca.gov/apex/f?p=401:56:5943774781817::NO:RP,57,RIR:P5_PROCEEDING_SELECT:'
            starting_link = link_str + self.list_of_docket_Ids[self.docket_Ids_Index]
            yield scrapy.Request(starting_link, dont_filter=True, method='GET', callback=self.parse_data)
            return
        yield scrapy.Request(starting_link, meta={"list_having_urls": list_having_urls, 'index': index,
                                    'dont_merge_cookies': True}, dont_filter=True, callback=self.parse_finalpage_data)