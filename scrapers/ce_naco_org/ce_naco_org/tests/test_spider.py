from scrapy.utils.test import get_crawler
from scrapy_tdd import *
import pytest

from ce_naco_org.spiders.ce_naco import CeNacoSpider

import ast

def response_from(file_name, url="http://ce.naco.org/?find=true/"):
    return mock_response_from_sample_file(my_path(__file__) + "/samples", file_name, url=url)

def describe_dnb_spider():
    to_test = CeNacoSpider()

    def describe_county_ids():
        resp = response_from("map.html")
    
        def should_return_county_ids():
            ids = to_test._extract_county_ids(resp)
            assert len(ids) == 3070 # original was 3138. Duplicates are removed.
    
        def should_return_county_requests():
            requests = to_test.parse_counties(resp)
            assert len(requests) == 3069 # county 99999 is now excluded as it is invalid.
            assert "js-https://ce.naco.org/?county_info=99999" not in requests

    def describe_benton_county_profile():
        resp = response_from("benton_county.html", url="js-https://ce.naco.org/?county_info=54015")
        resp.meta['id'] = '53005'
        resp.meta['county_url'] = "js-https://ce.naco.org/?county_info=54015"
        resp.meta['retry'] = 1
        result = to_test.parse_county_data(resp)

        def should_return_county_data():
            assert result['county_name'] == 'Benton County'
            assert result['county_state'] == 'WA'
            assert result['county_website_url'] == 'http://www.co.benton.wa.us'

    def describe_miner_county_profile():
        resp = response_from("miner_county.html", url="js-https://ce.naco.org/?county_info=46097")
        resp.meta['id'] = '46097'
        resp.meta['county_url'] = "js-https://ce.naco.org/?county_info=46097"
        resp.meta['retry'] = 1
        result = to_test.parse_county_data(resp)

        def should_return_county_data():
            assert result['county_name'] == 'Miner County'
            assert result['county_state'] == 'SD'
            assert result['county_website_url'] == 'https://www.minercountysd.org/'

    def describe_parsing_county_data():
        resp = response_from("county_missing_website_url.html", url="js-https://ce.naco.org/?county_info=28141")
        resp.meta['id'] = '28141'
        resp.meta['county_url'] = "js-https://ce.naco.org/?county_info=28141"
        resp.meta['retry'] = 1
        result = to_test.parse_county_data(resp)

        def should_return_website_url():
            assert result['county_website_url'] == ''


