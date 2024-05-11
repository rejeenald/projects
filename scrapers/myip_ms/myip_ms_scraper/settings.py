# -*- coding: utf-8 -*-

# Scrapy settings for myip_ms_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'myip_ms_scraper'

SPIDER_MODULES = ['myip_ms_scraper.spiders']
NEWSPIDER_MODULE = 'myip_ms_scraper.spiders'


SMALL_SAMPLE_MODE = True
COOKIES_ENABLED = False
COOKIES_DEBUG = True
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = CONCURRENT_REQUESTS

DOWNLOAD_TIMEOUT = 30

FEED_FORMAT = 'csv' # make CSV the default output format



DOWNLOAD_DELAY = 10 # Autothrottle never goes below this value and so we have to set it to low
AUTOTHROTTLE_ENABLED = False
AUTOTHROTTLE_DEBUG = True
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = CONCURRENT_REQUESTS




DOWNLOADER_MIDDLEWARES = {
    'orca_skips.proxy_net.ProxyNetMiddleware': 100,
    'orca_skips.rotate_user_agent.RotateUserAgentMiddleware' :400,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware' : None,
}

PROXY_USER = '9de8e524f7'
PROXY_PASSWORD = 'hHxvXVSN'

# this list might have to be updated from time to time ...
PROXY_SERVERS = [
'196.16.200.140:4444',
'196.17.200.18:4444',
'162.244.151.193:4444',
'196.18.200.122:4444',
'196.19.200.29:4444'
]
PROXY_LIST_STATIC = [PROXY_USER + ":" + PROXY_PASSWORD + "@" + proxy for proxy in PROXY_SERVERS]


PROXY_LIST_STATIC = ['residential-proxies.wordbean.com:17342']