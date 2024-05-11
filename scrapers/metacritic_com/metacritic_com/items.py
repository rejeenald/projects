# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
import scrapy
from scrapy.loader.processors import Join, Compose
from cherry_apples.processors.output import *
from collections import defaultdict


def strip_non_integers(in_list):
    return [re.sub('[^0-9.]+','', s).strip("") for s in in_list]

def convert_to_integer(value):
    try:
        score = int(value)
    except:
        score = float(value)
    return score
    
NUMBER = scrapy.Field(
	output_processor = Compose(
		strip_non_integers, remove_emptys, Join(' '),  convert_to_integer, 
		)
	)
DEFAULT = scrapy.Field(
	output_processor = Compose(
		strip_strings, remove_emptys, remove_duplicates, Join(' '),
		)
	)

LIST = scrapy.Field()

class MetacriticMovieItem(scrapy.Item):
    fields = defaultdict(lambda: DEFAULT)
    _values = defaultdict(list)
    
    def __setitem__(self, key, value):
        self._values[key] = value

    movie_id = DEFAULT
    movie_title = DEFAULT
    url_to_movie = DEFAULT
    studio = DEFAULT
    url_to_studio = DEFAULT
    release_date = DEFAULT
    src = DEFAULT
    movie_page_number = NUMBER

    # user reviews
    link_to_user_reviews = DEFAULT
    overall_user_score = DEFAULT # not set to NUMBER because there are string values (i.e. TBD)
    number_of_ratings = NUMBER
    positive_user_rating = NUMBER
    mixed_user_rating = NUMBER
    negative_user_rating = NUMBER
    
    # critic reviews
    link_to_critic_reviews = DEFAULT
    overall_critic_score = DEFAULT # not set to NUMBER because there are string values (i.e. TBD)
    number_of_critic_reviews = NUMBER
    positive_critic_rating = NUMBER
    mixed_critic_rating = NUMBER
    negative_critic_rating = NUMBER
   
class MovieReviewsItem(scrapy.Item):
    fields = defaultdict(lambda: DEFAULT)
    _values = defaultdict(list)
    
    def __setitem__(self, key, value):
        self._values[key] = value

    type_of_review = DEFAULT
    movie_id = DEFAULT
    src = DEFAULT
    appearance_order_of_review = NUMBER
    review_page_number = NUMBER
    rating = NUMBER
    username = DEFAULT
    url_of_reviewer = DEFAULT # some users do have urls linked to their profile
    posted_date_of_review = DEFAULT
    full_text_of_review = DEFAULT

    # NOT AVAILABLE ON CRITIC REVIEWS
    no_of_users_who_found_the_review_helpful = NUMBER
    total_users_voted_on_review = NUMBER
    
    # NOT AVAILABLE ON USER REVIEWS
    url_to_read_full_text_of_critic_review =DEFAULT
    
    




