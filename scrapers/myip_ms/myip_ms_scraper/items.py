# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join, Compose
from cherry_apples.processors.output import *
from collections import defaultdict


DEFAULT = scrapy.Field(
	output_processor = Compose(
		strip_strings, remove_emptys, remove_duplicates, Join(' '),
		)
	)

LIST = scrapy.Field()

class MyIPmsItem(scrapy.Item):
    ields = defaultdict(lambda: DEFAULT)
    _values = defaultdict(list)
    
    def __setitem__(self, key, value):
        self._values[key] = value
    
    number = DEFAULT
    website = DEFAULT
    website_ip_address = DEFAULT
    web_hosting_company_or_IP_owner = DEFAULT
    web_hosting_or_server_IP_location = DEFAULT
    web_hosting_city = DEFAULT
    world_site_popular_rating = DEFAULT
    website_popularity = DEFAULT
    IP_reverse_dns_host = DEFAULT
    top_level_hostname = DEFAULT
    web_hosting_state = DEFAULT
    dns_records = LIST
    record_update_time = DEFAULT
    src = DEFAULT
    
