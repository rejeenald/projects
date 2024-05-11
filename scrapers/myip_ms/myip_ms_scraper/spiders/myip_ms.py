# -*- coding: utf-8 -*-
import scrapy
import scrapy, json
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
import logging, requests
from ..items import MyIPmsItem
import random

class MyipMsSpider(CrawlSpider):
    name = 'myip_ms'
    url = 'https://myip.ms/browse/sites/1/own/376714'
    headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'en-US,en;q=0.9',
            # thats a cookie from page 1 to 200
            #'Cookie': 'PHPSESSID=rr2nopb0c8cjau081a06mbppg2; sw=121.3; sh=58.2; __gads=ID=035bcd30fedf1bfe:T=1588598509:S=ALNI_MYaYPLWh75tXBiWDAr3O_nILDVOhg; _ga=GA1.2.1086772129.1588598510; _gid=GA1.2.1819036842.1588598510; s2_csrf_cookie_name=ee0b648f5997de035e3b537d58fb2ca5; _gat=1; __unam=737437c-171dfd9937b-142d567e-8' \
            # that's a cookie for page 200 (works from page 1 to 4000?)
            'Cookie': 'PHPSESSID=ed991c063hqmhcc5eqj432v126; _ga=GA1.2.679825018.1588776345; _gid=GA1.2.575379143.1588776345; _gat=1; sh=371.2; s2_uGoo=b5a97c9e9ab6f3484eed97b8226002c557386529; s2_csrf_cookie_name=bb4f922d93a3b4611f23a03a48509777; s2_uLang=en; s2_theme_ui=red; sw=210.4; __unam=737437c-171ea733f5e-66566294-2'
        }

    def __init_(self, *args, **kwargs):
        super(MyipMsSpider, self).__init_(*args, **kwargs)
    
    def start_requests(self):
        return [Request(self.url, callback=self.parse_pages, headers=self.headers)]

    def parse_pages(self, response):
        logging.info(response.headers)
        logging.info("Start parsing page at: %s" % response.url)
        last_page_number = int(self._get_last_page_number(response))
        # last_page_number = 5
        return self.build_requests_for_pages(last_page_number, response)

    def _get_last_page_number(self, response):
        # logging.info("last page: %s", response.text)
        script_text = response.xpath("//script[contains(text(), 'paging_init')]/text()").extract_first()
        script_text = script_text.split(",")
        last_page_number = script_text[5].strip().strip("\'")
        logging.info("Extracting ... last page number: %s" % last_page_number)
        # last_page_number = response.xpath("//*[@class='aqPsites_tbl aqPaging']/a/text()")[-1].extract()
        return last_page_number

    def build_requests_for_pages(self, last_page_number, response):
        results = []
        logging.info("Parsing next page at: %s" % response.url)
        for page_number in range(last_page_number, 200, -1):
            url = 'https://myip.ms/browse/sites/{}/own/376714/'.format(page_number)
            results.append(Request(url, callback=self.parse_page_data, headers=self.headers, meta={'dont_merge_cookies': True}))
        #random.shuffle(results)
        return results
    
    def parse_page_data(self, response):
        results = []
        logging.info("Parsing page at: %s" % response.url)
        # logging.info("Robot? \n %s" % response.text)
        website_table_rows = response.xpath("//*[@id='sites_tbl']/tbody/tr")
        logging.info("Website table rows: %s" % str(website_table_rows))
        if len(website_table_rows) == 0:
            logging.warning("zero table rows at %s" % response.url)
            # TODO maybe we have to retry here ...
        for row in range(0, len(website_table_rows), 2):
            l = ItemLoader(MyIPmsItem(), response)
            l.add_value("src", response.url)
            self._extract_data_in_visible_row(l, row, website_table_rows)
            self._extract_data_in_toggled_row(l, row, website_table_rows)
            results.append(l.load_item())
        return results
        
    def _extract_data_in_visible_row(self, l, row, website_table_rows):
            number = website_table_rows[row].xpath("./td//text()").extract_first()
            l.add_value("number", number)
            row_data_visible = website_table_rows[row].xpath("./td/a/text()").extract()
            self._add_item_values(row_data_visible, l)
            world_site_popular_rating = website_table_rows[row].xpath("./td/span/text()").extract_first()
            l.add_value("world_site_popular_rating", world_site_popular_rating)
    
    def _add_item_values(self, row_data_visible, l):
            l.add_value("website", row_data_visible[0])
            l.add_value("website_ip_address", row_data_visible[1])
            l.add_value("web_hosting_company_or_IP_owner", row_data_visible[2])
            l.add_value("web_hosting_or_server_IP_location", row_data_visible[3])
            l.add_value("web_hosting_city", row_data_visible[4])

    def _extract_data_in_toggled_row(self, l, row, website_table_rows):
            website_popularity = website_table_rows[row+1].xpath(\
                "./td//b[contains(text(), 'Website Popularity:')]\
                    /parent::div/following::div[@class='sval'][position()=1]//text()").extract()
            website_popularity = "".join(website_popularity)
            l.add_value("website_popularity", website_popularity)

            IP_reverse_dns_host = website_table_rows[row+1].xpath(\
                "./td//b[contains(text(), 'IP Reverse DNS (Host):')]\
                    /parent::div/following::div[@class='sval'][position()=1]//text()").extract()
            l.add_value("IP_reverse_dns_host", IP_reverse_dns_host)

            top_level_hostname = website_table_rows[row+1].xpath(\
                "./td//b[contains(text(), 'Top Level Hostname:')]\
                    /parent::div/following::div[@class='sval'][position()=1]//text()").extract()
            l.add_value("top_level_hostname", top_level_hostname)

            web_hosting_state = website_table_rows[row+1].xpath(\
                "./td//b[contains(text(), 'Web Hosting State:')]\
                    /parent::div/following::div[@class='sval'][position()=1]//text()").extract()
            l.add_value("web_hosting_state", web_hosting_state)

            dns_records = website_table_rows[row+1].xpath(\
                "./td//b[contains(text(), 'DNS Records:')]\
                    /parent::div/following::div[@class='sval'][position()=1]/a/text()").extract()
            l.add_value("dns_records", dns_records)

            record_update_time = website_table_rows[row+1].xpath(\
                "./td//b[contains(text(), 'Record Update Time:')]\
                    /parent::div/following::div[@class='sval'][position()=1]/text()").extract()
            l.add_value("record_update_time", record_update_time)