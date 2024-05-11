# Scrapy settings for metacritic_com project
#=========================================================================================
# basic settings for scrapy
#=========================================================================================
BOT_NAME = 'metacritic_com'
SPIDER_MODULES = ['metacritic_com.spiders']
NEWSPIDER_MODULE = 'metacritic_com.spiders'

SMALL_SAMPLE_MODE = False
COOKIES_ENABLED = False
COOKIES_DEBUG = True
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = CONCURRENT_REQUESTS

DOWNLOAD_TIMEOUT = 600

FEED_FORMAT = 'csv' # make CSV the default output format
# Retry many times since proxies often fail
RETRY_TIMES = 50
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 502, 503, 504, 429, 400, 403, 404, 408, 429, 470, 999]
#=========================================================================================


#=========================================================================================
# settings for network proxies
#=========================================================================================
PROXY_TYPE = 'dedicated'

if PROXY_TYPE == 'dedicated':

    DOWNLOADER_MIDDLEWARES = {
        'orca_skips.proxy_net.ProxyNetMiddleware': 100,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware' : None,
        'orca_skips.rotate_user_agent.RotateUserAgentMiddleware' :400,
        # 'cherry_apples.middlewares.debugging.DebuggingMiddleware': 710,
        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    }

    # use our non-rotating dedicated proxies
    PROXY_LIST_STATIC = [ "us-dedicated-proxies.done-data-solutions.com:%d" % port for port in range(37652, 37692) ]
    PROXY_DROP_FAILED = False

elif PROXY_TYPE == 'residential':

    DOWNLOADER_MIDDLEWARES = {
        'orca_skips.proxy_net.ProxyNetMiddleware': 100,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware' : None,
        'orca_skips.rotate_user_agent.RotateUserAgentMiddleware' :400,
        # 'cherry_apples.middlewares.debugging.DebuggingMiddleware': 710,
        'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    }

    # use our non-rotating dedicated proxies
    PROXY_LIST_STATIC = [ "residential-proxies.done-data-solutions.com:%d" % port for port in range(17343, 17353) ]
    PROXY_DROP_FAILED = False
#=========================================================================================

#=========================================================================================
# settings for cherry apples
#=========================================================================================
MULTI_FILES = {
    'MetacriticMovieItem': {'FILENAME': 'movie_details'},
    'MovieReviewsItem': {'FILENAME': 'movie_reviews'}
}

ITEM_PIPELINES = {
    'cherry_apples.pipelines.multi_item_output_pipeline.MultiItemOutputPipeline': 300
}
