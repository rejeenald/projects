import scrapy
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider

from ..items import MetacriticMovieItem, MovieReviewsItem

import logging

class MetacriticSpider(CrawlSpider):
    name = 'metacritic'
    movie_urls_per_year = []
    movie_id = ''

    def __init__(self, *args, **kwargs):
        super(MetacriticSpider, self).__init__(*args, **kwargs)
        self.movie_urls_per_year = self.build_movies_urls()

    def build_movies_urls(self):
        movie_urls = []
        for year in range(2005, 2020):
            movie_urls.append("https://www.metacritic.com/browse/movies/score/metascore/year/filtered?year_selected={}"\
                .format(year))
        return movie_urls

    def start_requests(self):
        results = []
        logging.info("SMALL SAMPLE MODE: %s" % self.settings.get('SMALL_SAMPLE_MODE')) 
        if self.settings.get('SMALL_SAMPLE_MODE'):
            # used 2019 because the movie "parasite" is in year 2019 and its user reviews have next pages.
            self.movie_urls_per_year = ["https://www.metacritic.com/browse/movies/score/metascore/year/filtered?year_selected=2019"]
            logging.info("Will be extracting movies of 2018 ONLY!")

        for movies_url in self.movie_urls_per_year:
            results.append(Request(movies_url, callback=self.parse_movie_urls, meta={'movie_page_number': 1}))
        return results
        
    def parse_movie_urls(self, response):
        logging.info("Parsing movie urls in page %s..." % response.meta['movie_page_number'])
        meta = response.meta
        requests = []
        _movie_link_extractor = LinkExtractor(unique=True, restrict_xpaths=("//table//a[@class='title']"))
        for movie_link in _movie_link_extractor.extract_links(response):
            meta['movie_id'] = movie_link.url.split("/")[-1]
            # movie_request_urls = {'movie': movie_link.url}
            movie_request_urls = {}
            movie_request_urls['reviews'] = ["/".join([movie_link.url, 'user-reviews'])]
            movie_request_urls['reviews'].append("/".join([movie_link.url, 'critic-reviews']))

            for key in movie_request_urls.keys():
                if key == 'movie':
                    requests.append(Request(movie_link.url, callback=self.parse_movie_details, meta=meta))
                else:
                    for review_url in movie_request_urls[key]:
                        response.meta['review_page_number'] = 1
                        requests.append(Request(review_url, callback=self.parse_movie_reviews, meta=meta))
            
        next_page_url = self.build_next_page_movie_url(response)
        if next_page_url != None:
            requests.append(next_page_url)
        return requests

    def parse_movie_details(self, response):
        logging.info("Parsing movie details of movie id %s..." % response.meta['movie_id'])
        meta = response.meta
        results = []
        movie_item = ItemLoader(MetacriticMovieItem(), response)
        movie_item.add_value('movie_id', meta['movie_id'])
        movie_item.add_xpath('movie_title', "//*[contains(@class, 'product_page_title')]//h1/text()")
        movie_item.add_value('url_to_movie', response.url)
        movie_item.add_xpath("movie_page_number", str(response.meta['movie_page_number']))
        movie_item.add_xpath('release_date', "//*[contains(text(), 'Release Date')]/following-sibling::span/text()")
        movie_item.add_value('src', response.url)

        studio = response.xpath("//*[@class='distributor']/a/text()").extract_first()
        if studio:
            movie_item.add_value('studio', studio)
            url_to_studio = response.xpath("//*[@class='distributor']/a/@href").extract_first()
            movie_item.add_value('url_to_studio', "".join(['https://www.metacritic.com', url_to_studio]))
        
        self.parse_score_distribution(movie_item, response)
        results.append(movie_item.load_item())
        return results

    def parse_score_distribution(self, movie_item, response):
        score_distributions_selectors = response.xpath("//*[@class='distribution']")
        for score_distributions_sel in score_distributions_selectors:
            link_to_reviews = score_distributions_sel.xpath(".//*[@class='score fl']//@href").extract_first()
            score = score_distributions_sel.xpath(".//*[@class='score fl']//div/text()").extract_first()
            positive = score_distributions_sel.xpath(".//*[@class='chart positive']//div[@class='count fr']/text()").extract_first()
            mixed = score_distributions_sel.xpath(".//*[@class='chart mixed']//div[@class='count fr']/text()").extract_first()
            negative = score_distributions_sel.xpath(".//*[@class='chart negative']//div[@class='count fr']/text()").extract_first()

            if 'user-reviews' in link_to_reviews:
                movie_item.add_value('link_to_user_reviews', "".join(["https://www.metacritic.com", link_to_reviews]))
                movie_item.add_value("overall_user_score", score)
                movie_item.add_value("positive_user_rating", positive)
                movie_item.add_value("mixed_user_rating", mixed)
                movie_item.add_value("negative_user_rating", negative)
                total_ratings_or_reviews = movie_item.get_output_value("positive_user_rating")\
                     + movie_item.get_output_value("mixed_user_rating")\
                          + movie_item.get_output_value("negative_user_rating")
                movie_item.add_value("number_of_ratings", str(total_ratings_or_reviews))
                
            else:
                movie_item.add_value('link_to_critic_reviews', "".join(["https://www.metacritic.com", link_to_reviews]))
                movie_item.add_value("overall_critic_score", score)
                movie_item.add_value("positive_critic_rating", positive)
                movie_item.add_value("mixed_critic_rating", mixed)
                movie_item.add_value("negative_critic_rating", negative)
                total_ratings_or_reviews = movie_item.get_output_value("positive_critic_rating")\
                     + movie_item.get_output_value("mixed_critic_rating")\
                          + movie_item.get_output_value("negative_critic_rating")
                movie_item.add_value("number_of_critic_reviews", str(total_ratings_or_reviews))
            
    def parse_movie_reviews(self, response):
        # user reviews are sorted by default in 'most helpful' to 'least helpful' reviews
        # critic reviews are sorted by critic score in descending order
        logging.info("Parsing movie reviews in page %s..." % response.meta['review_page_number'])
        results = []
        reviewer_counter = 1

        review_selectors = response.xpath("//*[contains(@class,'review pad_top1') and not(contains(@id, 'native_top'))]")
        for review_sel in review_selectors:
            review_item = ItemLoader(MovieReviewsItem(), response)
            review_item.add_value('movie_id', response.meta['movie_id'])
            review_item.add_value('src', response.url)
            review_item.add_value('appearance_order_of_review', str(reviewer_counter))
            review_item.add_value('review_page_number', str(response.meta['review_page_number']))

            review_details = self.extract_all_reviews(review_sel, response.url)
            review_item.add_value("rating", review_details['rating'])
            review_item.add_value("username", review_details['username'])
            review_item.add_value("posted_date_of_review", review_details['posted_date_of_review'])
            review_item.add_value("url_of_reviewer", review_details['url_of_reviewer'])
            review_item.add_value("full_text_of_review", review_details['full_text_of_review'])
            review_item.add_value("type_of_review", review_details['type_of_review'])

            if review_details['type_of_review'] == 'User Review':
                review_item.add_value("no_of_users_who_found_the_review_helpful", review_details['no_of_users_who_found_the_review_helpful'])
                review_item.add_value("total_users_voted_on_review", review_details['total_users_voted_on_review'])
            else:
                review_item.add_value("url_to_read_full_text_of_critic_review", review_details['url_to_read_full_text_of_critic_review'])

            results.append(review_item.load_item())
            reviewer_counter = reviewer_counter + 1
        
        next_page_url = self.build_next_page_review_url(response)
        if next_page_url != None:
            results.append(next_page_url)
        return results

    def extract_all_reviews(self, review_sel, review_url):
        type_of_review = self.get_type_of_review(review_url)
        review = {}
        review['type_of_review'] = type_of_review
        review['rating'] = review_sel.xpath(".//div[contains(@class, 'metascore_w')]//text()").extract_first()
        review['username'] = review_sel.xpath(".//*[@class='author']//text()").extract_first()
        review['posted_date_of_review'] = review_sel.xpath(".//*[@class='date']//text()").extract_first()
            
        url_of_reviewer = review_sel.xpath(".//*[@class='author']/a/@href").extract_first()
        if url_of_reviewer:
            review['url_of_reviewer'] = "".join(["https://www.metacritic.com", url_of_reviewer])
        else:
            review['url_of_reviewer'] = ''

        if type_of_review == 'User Review':
            review['no_of_users_who_found_the_review_helpful'] = review_sel.xpath(".//*[@class='yes_count']/text()").extract_first()
            review['total_users_voted_on_review'] = review_sel.xpath(".//*[@class='total_count']/text()").extract_first()

        return self.get_review_full_text(review_sel, review)
    
    def get_type_of_review(self, review_url):
        if 'user-review' in review_url:
            return 'User Review'
        else:
            return 'Critic Review'

    def get_review_full_text(self, review_sel, review):
        if review['type_of_review'] == 'User Review':
            user_review_expand_toggle = review_sel.xpath(".//*[@class='review_body']//span[contains(text(), 'Expand')]")
            if user_review_expand_toggle:
                review["full_text_of_review"] = review_sel.xpath(".//*[@class='blurb blurb_expanded']/text()").extract()
            else:
                review["full_text_of_review"] = review_sel.xpath(".//*[@class='review_body']//text()").extract()
        else:
            read_full_critic_review_url = review_sel.xpath(".//*[@class='read_full']/@href").extract_first()
            if read_full_critic_review_url:
                review["full_text_of_review"] = review_sel.xpath(".//*[@class='summary']/a[@class='no_hover']//text()").extract()
                review["url_to_read_full_text_of_critic_review"] = read_full_critic_review_url
            else:
                review["full_text_of_review"] = review_sel.xpath(".//*[@class='summary']//text()").extract()
                review["url_to_read_full_text_of_critic_review"] = ''

        return review

    def build_next_page_movie_url(self, response):
        next_page_url = response.xpath("//*[@class='action'][@rel='next']/@href").extract_first()
        logging.info("Extracting next page url...")
        if next_page_url:
            page_number = response.meta['movie_page_number'] + 1
            meta = response.meta
            meta['movie_page_number'] = page_number
            if self.settings.get('SMALL_SAMPLE_MODE'):
                if page_number > 2:
                    logging.info("Stopped the extraction of movies after page 2.")
                else:
                    next_page_url = "".join(['https://www.metacritic.com', next_page_url])
                    return Request(next_page_url, callback=self.parse_movie_urls, meta=meta)
            else:
                next_page_url = "".join(['https://www.metacritic.com', next_page_url])
                return Request(next_page_url, callback=self.parse_movie_urls, meta=meta)

    def build_next_page_review_url(self, response):
        next_page_url = response.xpath("//*[@class='action'][@rel='next']/@href").extract_first()
        logging.info("Extracting next page url...")
        if next_page_url:
            page_number = response.meta['review_page_number'] + 1
            meta = response.meta
            meta['review_page_number'] = page_number
            if self.settings.get('SMALL_SAMPLE_MODE'):
                if page_number > 2:
                    logging.info("Stopped the extraction of reviews after page 2.")
                else:
                    next_page_url = "".join(['https://www.metacritic.com', next_page_url])
                    return Request(next_page_url, callback=self.parse_movie_reviews, meta=meta)
            else:
                next_page_url = "".join(['https://www.metacritic.com', next_page_url])
                return Request(next_page_url, callback=self.parse_movie_reviews, meta=meta)
           