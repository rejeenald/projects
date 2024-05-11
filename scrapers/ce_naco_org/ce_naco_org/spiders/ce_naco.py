import time
import logging
import traceback

import scrapy
import scrapy
from scrapy.http import Request
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapyium.scrapyium_request import ScrapyiumRequest
from scrapyium import RescueRequestDataException
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

from ce_naco_org.items import CeNacoOrgItem


class CeNacoSpider(scrapy.Spider):
    name = 'ce_naco'
    
    def start_requests(self):
        url = "js-http://ce.naco.org/?find=true"

        logging.info("Visiting the page: %s" % url)
        return [ScrapyiumRequest(url, callback=self.parse_counties, errback=self._on_error, dont_filter=True)]
            
    def parse_counties(self, response):
        logging.info("Parsing counties now.")
        requests = []
        url = "https://ce.naco.org/?county_info="
        county_ids = self._extract_county_ids(response)
        for id in county_ids:
            if str(id) == '99999':
                logging.info("Skipping invalid county id")
                continue

            county_url = "js-" + url + str(id)
            meta = {"id": id, 'county_url': county_url, 'retry': 1}
            requests.append(ScrapyiumRequest(county_url, callback=self.parse_county_data, meta=meta, 
                navigate_cb=self.navigate_county_page, errback=self._on_error))
        return requests

    def navigate_county_page(self, response, scrapyium):
        logging.info("Trying to navigate county page...")
        if not response.xpath('//*[@class="value county-info-var-County_Website"]//a[1]/@href'):
            logging.info("We did not get the url, so we will wait and scroll down")
            scrapyium.natural_wait(5)
            scrapyium.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            scrapyium.natural_wait(5)

    def parse_county_data(self, response):
        meta = response.meta
        county_id = str(meta['id'])
        if 'county_info' in response.url:
            logging.info("Received expected response for county id %s from this country url: %s." % (county_id, response.url))
            name_state = response.xpath("//*[@class='profile-county-name']/text()").extract_first()
            if not name_state:
                logging.warning("Name and state cannot be extracted for county id %s." % county_id)
                return self._retry_request(meta)
            return self._load_county_data(name_state, response, meta)
        else:
            logging.warning("Got the unexpected response for a county id %s from this redirect url: %s" % (county_id, response.url))
            return self._retry_request(meta)

    def _load_county_data(self, name_state, response, meta):
        l = ItemLoader(CeNacoOrgItem(), response)
        name_state = name_state.split(", ")
        l.add_value("county_name", name_state[0])
        l.add_value("county_state", name_state[1])
        l.add_value('src', response.url)
        l.add_value("id", str(meta['id']))
        l.add_value('retry', str(meta['retry']))
        county_website_url = response.xpath('//*[@class="value county-info-var-County_Website"]//a[1]/@href').extract_first()
        l.add_value("county_website_url", county_website_url)
        if not county_website_url:
            logging.warning("We still did not get a website url. Please check here html")
            logging.info(response.text)
        return l.load_item()

    def _retry_request(self, meta):
        meta['retry'] = meta['retry'] + 1
        logging.info("Retrying request for country url %s of county id %s" % (meta['county_url'], meta['id']))
        return ScrapyiumRequest(meta['county_url'], callback=self.parse_county_data, meta=meta, errback=self._on_error, dont_filter=True)

    def _extract_county_ids(self, response):
        county_ids = response.xpath("//*[@class='svg-county']/@id").extract()
        logging.info("There are %s county ids, but duplicates will be removed." % len(county_ids))
        county_ids = list(dict.fromkeys(county_ids))
        print(len(county_ids))
        logging.info("Duplicates are removed if there is any. There are %s county ids." % len(county_ids))
        return county_ids

    def _on_error(self, failure):
        rescued_url, rescued_meta, error_message = self._extract_data_from_failure(failure)

        if len(error_message) > 0:
            logging.error(error_message)
        
        if not rescued_url:
            log_message = "Cannot retry rescued_url request because it has no value (i.e. NoneType)."
            logging.error(log_message)
            return
            
        logging.info("Retrying failed homepage map url: %s" % rescued_url)
        rescued_meta['retry'] = rescued_meta['retry'] + 1
        logging.info("Increasing retry.")
        
        if "county_info" in rescued_url:
            return Request(rescued_url, callback=self.parse_county_data, 
                                    meta=rescued_meta,
                                    errback=self._on_error, dont_filter=True)
        else:
            return Request(rescued_url, callback=self.parse_counties, 
                            meta=rescued_meta, errback=self._on_error, dont_filter=True)
        
    def _extract_data_from_failure(self, failure):
        response, request = None, None
        error_message = ''
        if failure.check(HttpError):
            response = failure.value.response
            error_message = 'HttpError on %s' % response.url
        elif failure.check(DNSLookupError):
            request = failure.request
            error_message = 'DNSLookupError on %s' % request.url
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            error_message = 'TimeoutError on %s' % request.url
        elif failure.check(RescueRequestDataException):
            request = failure.value.request            
            error_message = 'RescueRequestDataException on %s', request.url

        if response:
            return response.url, response.meta, error_message
        elif request:
            return request.url, request.meta, error_message
        else:
            return None, dict(), error_message


    



