# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose, Compose, TakeFirst
from cherry_apples.processors.output import *

DEFAULT = scrapy.Field(
	output_processor = Compose(
		strip_strings, remove_emptys, Join(' '),
		)
	)

def fix_null_href(text):
    if text == 'null':
        text = ''
    return text

class CeNacoOrgItem(scrapy.Item):
    src = DEFAULT
    id = DEFAULT
    retry = DEFAULT
    county_name = DEFAULT
    county_state = DEFAULT
    county_website_url = scrapy.Field(
        output_processor = Compose(
            strip_strings, remove_emptys, Join(' '), fix_null_href,
            )
	)
