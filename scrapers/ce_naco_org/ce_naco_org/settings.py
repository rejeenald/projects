# Scrapy settings for ce_naco_org project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ce_naco_org'

SPIDER_MODULES = ['ce_naco_org.spiders']
NEWSPIDER_MODULE = 'ce_naco_org.spiders'
SMART_SAMPLE_ACTIVE= False
SMART_SAMPLE_SIZE = 500

COOKIES_ENABLED = False
DOWNLOAD_DELAY = 10
CONCURRENT_REQUESTS = 5
CONCURRENT_REQUESTS_PER_DOMAIN = CONCURRENT_REQUESTS

DOWNLOAD_TIMEOUT = 100

FEED_FORMAT = 'csv' # make CSV the default output format
# Retry many times since proxies often fail
RETRY_TIMES = 50
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 502, 503, 504, 429, 400, 403, 404, 408, 429, 470, 999]
#=========================================================================================

#scrapyium settings
SELENIUM_INJECT_EXTENSION = True
RUN_SELENIUM_IN_BACKGROUND = True
SELENIUM_WAIT_SECONDS = 10
SELENIUM_WAIT_MULTIPLICATOR = 1.0
DUMP_SELENIUM_LOGS = False
SELENIUM_DEBUG_OUTPUT = False
SCRAPYIUM_CONCURRENT_REQUESTS = int(CONCURRENT_REQUESTS * 2)
SCRAPYIUM_MAX_UNNAMED_SESSIONS = int(CONCURRENT_REQUESTS * 2)
SCRAPYIUM_IMPLICITLY_WAIT_SECONDS = 20

# DOWNLOAD_DELAY = .1 # Autothrottle never goes below this value and so we have to set it to low
# AUTOTHROTTLE_ENABLED = False
# AUTOTHROTTLE_DEBUG = True
# AUTOTHROTTLE_MAX_DELAY = 10.0
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1
LOG_LEVEL = "INFO"
# DEBUG_DUMP = True # Set this to False if you do not want to save requests and responses data to file
# DEBUG_DUMP_DIRECTORY = './debugging_dumps'


DOWNLOAD_HANDLERS = {
    'js-http': 'scrapyium.scrapyium_downloader.ScrapyiumDownloader',
    'js-https': 'scrapyium.scrapyium_downloader.ScrapyiumDownloader',
    'scrapyium': 'scrapyium.scrapyium_downloader.ScrapyiumDownloader', # for using management methods
}

DOWNLOADER_MIDDLEWARES = {
        'orca_skips.proxy_net.ProxyNetMiddleware': 100,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware' : None,
        'orca_skips.rotate_user_agent.RotateUserAgentMiddleware' :400,
        # 'cherry_apples.middlewares.debugging.DebuggingMiddleware': 710,
        'cherry_apples.middlewares.SmartSampleMiddleware': 543,
        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    }


# DEBUG_DUMP = True # enables / disables full request/response dumping
# DEBUG_DUMP_DIRECTORY = './debugging_dumps' # where to put the request/response dump files
# DEBUG_CONVERT_TO_CURL = True # enable printing command lines for each request


# use our non-rotating dedicated proxies
# PROXY_TYPE = 'dedicated'
PROXY_LIST_STATIC = [ "us-dedicated-proxies.done-data-solutions.com:%d" % port for port in range(37652, 37692) ]
#PROXY_LIST_STATIC += [ "residential-proxies.done-data-solutions.com:%d" % port for port in range(17343, 17353) ]
PROXY_DROP_FAILED = False