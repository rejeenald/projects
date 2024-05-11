import os, logging, pkg_resources, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')))
from datetime import datetime

from scrapy_tdd import *
from scrapy.utils.test import get_crawler

from metacritic_com.spiders.metacritic import MetacriticSpider

import pytest

def response_from(file_name, url="https://www.metacritic.com/movie", meta=None):
    return mock_response_from_sample_file(my_path(__file__) + "/samples", file_name, url=url, meta=meta)

def describe_profile_spider():
    to_test = MetacriticSpider.from_crawler(get_crawler())

    def describe_movie_urls_per_year():
        movie_urls_per_year = to_test.build_movies_urls()

        def should_return_movie_urls_per_year():
            assert len(movie_urls_per_year) == 15
            assert "https://www.metacritic.com/browse/movies/score/metascore/year/filtered?year_selected=2005" in movie_urls_per_year
            assert "https://www.metacritic.com/browse/movies/score/metascore/year/filtered?year_selected=2019" in movie_urls_per_year
            assert "https://www.metacritic.com/browse/movies/score/metascore/year/filtered?year_selected=2020" not in movie_urls_per_year

    def describe_movie_urls_in_a_page():
        resp = response_from("Best Movies for 2005 - Metacritic.html")
        resp.meta['movie_page_number'] = 1
        movie_list_in_a_page = to_test.parse_movie_urls(resp)
        movie_reviews_urls = urls_from_requests(movie_list_in_a_page)

        def should_return_movie_urls_in_a_page():
            # assert len(movie_reviews_urls) == 301

            # movies only
            # assert len(movie_reviews_urls) == 101

            # reviews only
            assert len(movie_reviews_urls) == 201
    
        def describe_next_page_for_movies():
            next_page = to_test.build_next_page_movie_url(resp)

            def should_return_next_page_request_for_movies():
                assert next_page

        def describe_no_next_page_for_movies():
            resp = response_from("no next page - Best Movies for 2005 - Page 6 - Metacritic.html")
            next_page = to_test.build_next_page_movie_url(resp)

            def should_return_no_next_page_request_for_movies():
                assert not next_page

    
    def describe_movie_basic_details_1():
        resp = response_from("Turtles Can Fly Reviews - Metacritic.html", url="https://www.metacritic.com/movie/turtles-can-fly")
        resp.meta['movie_page_number'] = 1
        resp.meta['movie_id'] = 'turtles-can-fly'
        results = to_test.parse_movie_details(resp)[0]

        def should_return_number_of_item_data_1():
            assert len(results) == 20

        def should_return_movie_basic_details_1():
            assert results['movie_id'] == 'turtles-can-fly'
            assert results['movie_title'] == 'Turtles Can Fly'
            assert results['url_to_movie'] == 'https://www.metacritic.com/movie/turtles-can-fly'
            assert results['studio'] == 'IFC Films'
            assert results['url_to_studio'] == 'https://www.metacritic.com/company/ifc-films'
            assert results['release_date'] == 'February 18, 2005'
            assert results['src'] == 'https://www.metacritic.com/movie/turtles-can-fly'
            assert results['movie_page_number'] == 1.0
        
            # user reviews overall scores
            assert results['link_to_user_reviews'] == 'https://www.metacritic.com/movie/turtles-can-fly/user-reviews'
            assert results['overall_user_score'] == '8.7'
            assert results['number_of_ratings'] == 112
            assert results['positive_user_rating'] == 101
            assert results['mixed_user_rating'] == 1
            assert results['negative_user_rating'] == 10
            
            # critic reviews overall scores
            assert results['link_to_critic_reviews'] == 'https://www.metacritic.com/movie/turtles-can-fly/critic-reviews'
            assert results['overall_critic_score'] == '85'
            assert results['number_of_critic_reviews'] == 31
            assert results['positive_critic_rating'] == 30
            assert results['mixed_critic_rating'] == 1
            assert results['negative_critic_rating'] == 0

    def describe_movie_scores_with_integer_issue_on_score_distribution():
        resp = response_from("Promare Reviews - Metacritic.html", url="https://www.metacritic.com/movie/promare")
        resp.meta['movie_page_number'] = 2
        resp.meta['movie_id'] = 'promare'
        results = to_test.parse_movie_details(resp)[0]

        def should_return_number_of_item_data_2_with_integer_issue_on_score_distribution():
            assert len(results) == 20

        def should_return_movie_scores_with_integer_issue_on_score_distribution():
            # user reviews overall scores
            assert results['overall_user_score'] == '10'
            assert results['number_of_ratings'] == 1159
            assert results['positive_user_rating'] == 1155
            assert results['mixed_user_rating'] == 2
            assert results['negative_user_rating'] == 2
            
            # critic reviews overall scores
            assert results['overall_critic_score'] == '77'
            assert results['number_of_critic_reviews'] == 8
            assert results['positive_critic_rating'] == 8
            assert results['mixed_critic_rating'] == 0
            assert results['negative_critic_rating'] == 0
            
    
    def describe_extracted_user_reviews():
        resp = response_from("user - Read User Reviews and Submit your own for Inside Out (2015) - Metacritic.html", url="https://www.metacritic.com/movie/inside-out-2015/user-reviews")
        resp.meta['review_page_number'] = 1
        resp.meta['movie_id'] = 'inside-out-2015'
        review = to_test.parse_movie_reviews(resp)[0]
    
        @pytest.mark.skip('merge with rej')
        def should_return_number_of_item_reviews():
            assert len(review) == 12

        @pytest.mark.skip('merge with rej')
        def should_return_movie_user_reviews_1():
            assert review['type_of_review'] == 'User Review'
            assert review['movie_id'] == 'inside-out-2015'
            assert review['src'] == "https://www.metacritic.com/movie/inside-out-2015/user-reviews"
            assert review['appearance_order_of_review'] == 1
            assert review['review_page_number'] == 1
            assert review['rating'] == 10
            assert review['username'] == 'kevtheobald'
            assert review['url_of_reviewer'] == 'https://www.metacritic.com/user/kevtheobald'
            assert review['posted_date_of_review'] == 'Jun 19, 2015'
            assert review['full_text_of_review'].startswith("Pixar finally broke out of the Pixar mold")
            assert review['no_of_users_who_found_the_review_helpful'] == 54
            assert review['total_users_voted_on_review'] == 64

    def describe_extracted_critic_reviews():
        resp = response_from("Critic Reviews for Inside Out (2015) - Metacritic.html", url="https://www.metacritic.com/movie/inside-out-2015/critic-reviews")
        resp.meta['review_page_number'] = 1
        resp.meta['movie_id'] = 'inside-out-2015'
        review = to_test.parse_movie_reviews(resp)[0]       

        def should_return_number_of_item_reviews():
            assert len(review) == 11

        def should_return_movie_critic_review_of_a_reviewer():
            assert review['type_of_review'] == 'Critic Review' 
            assert review['movie_id'] == 'inside-out-2015'
            assert review['src'] == "https://www.metacritic.com/movie/inside-out-2015/critic-reviews"
            assert review['appearance_order_of_review'] == 1
            assert review['review_page_number'] == 1
            assert review['rating'] == 100
            assert review['username'] == 'Moira Macdonald'
            assert review['url_of_reviewer'] == 'https://www.metacritic.com/critic/moira-macdonald?filter=movies'
            assert review['posted_date_of_review'] == 'Jul 8, 2017'
            assert review['full_text_of_review'].startswith("Inside Out movingly but casually plays with our emotions")
            assert review['url_to_read_full_text_of_critic_review'] == "http://www.seattletimes.com/entertainment/movies/inside-out-pixars-latest-is-a-real-head-trip/"
            
                
    def describe_next_page_for_movie_reviews():
        resp = response_from("reviews with next page - Read User Reviews and Submit your own for Parasite - Page 2 - Metacritic.html")
        resp.meta['review_page_number'] = 1
        next_page = to_test.build_next_page_review_url(resp)

        @pytest.mark.skip('merge with rej')
        def should_return_next_page_request_for_movie_reviews():
            assert next_page

    def describe_no_next_page_for_movie_reviews():
        resp = response_from("Critic Reviews for Inside Out (2015) - Metacritic.html")
        next_page = to_test.build_next_page_review_url(resp)

        def should_return_no_next_page_request_for_movie_reviews():
            assert not next_page

    def describe_critic_reviews_numbering_1():
        resp = response_from("Critic Reviews for Inside Out (2015) - Metacritic.html", url="https://www.metacritic.com/movie/inside-out-2015/critic-reviews")
        resp.meta['review_page_number'] = 1
        resp.meta['movie_id'] = 'inside-out-2015'
        reviews = to_test.parse_movie_reviews(resp)
        order_numbers = [review['appearance_order_of_review'] for review in reviews]

        def should_return_number_of_critic_reviews_and_numbering_1():
            assert len(reviews) == 55
            assert order_numbers[0] == 1
            assert order_numbers[-1] == 55


    def describe_critic_reviews_numbering_2():
        resp = response_from("Critic Reviews for My Summer of Love - Metacritic.html")
        resp.meta['review_page_number'] = 1
        resp.meta['movie_id'] = 'my-summer-of-love'
        reviews = to_test.parse_movie_reviews(resp)
        order_numbers = [review['appearance_order_of_review'] for review in reviews]

        def should_return_number_of_critic_reviews_and_numbering_2():
            assert len(reviews) == 31
            assert order_numbers[0] == 1
            assert order_numbers[-1] == 31

    def describe_no_missing_user_reviews():
        resp = response_from("no missing text - Read User Reviews and Submit your own for My Summer of Love - Metacritic.html", url="https://www.metacritic.com/movie/my-summer-of-love/user-reviews")
        resp.meta['review_page_number'] = 1
        resp.meta['movie_id'] = 'my-summer-of-love'
        reviews = to_test.parse_movie_reviews(resp)

        def should_return_number_of_user_reviews():
            assert len(reviews) == 14

        def describe_review_text_with_expand_toggle():
            review = reviews[0]
        
            def should_return_review_text_with_expand_toggle():
                assert review['username'] == 'ERG1008'
                assert review['full_text_of_review'].startswith("Two girls from different backgrounds meet one Summer")

        def describe_review_text_with_no_expand_toggle():
            review = reviews[2]
        
            def should_return_rreview_text_with_no_expand_toggle():
                assert review['username'] == 'LeatherT.'
                assert review['full_text_of_review'].startswith("I walked out of the movie wishing to strangle the people")

    def describe_no_missing_critic_reviews():
        resp = response_from("no missing text - Critic Reviews for Brokeback Mountain - Metacritic.html", url="https://www.metacritic.com/movie/brokeback-mountain/critic-reviews")
        resp.meta['review_page_number'] = 1
        resp.meta['movie_id'] = 'brokeback-mountain'
        reviews = to_test.parse_movie_reviews(resp)

        def should_return_number_critic_of_reviews():
            assert len(reviews) == 41

        def describe_review_text_with_read_full_link():
            review = reviews[0]
        
            def should_return_rreview_text_with_read_full_link():
                assert review['username'] == 'David Ansen'
                assert review['full_text_of_review'].startswith("There's neither coyness nor self-importance in Brokeback Mountain--just close,")

        def describe_review_text_with_no_read_full_link():
            review = reviews[14]
        
            def should_return_rreview_text_with_no_read_full_link():
                assert review['username'] == 'Joe Morgenstern'
                assert review['full_text_of_review'].startswith("Brokeback Mountain aspires to an epic sweep and achieves it,")

    def describe_no_duplicate_full_text_user_review():
        resp = response_from("full user review - Read User Reviews and Submit your own for Superman Returns - Metacritic.html", url="https://www.metacritic.com/movie/superman-returns/user-reviews")
        resp.meta['review_page_number'] = 1
        resp.meta['movie_id'] = 'superman-returns'
        reviews = to_test.parse_movie_reviews(resp)


        def describe_no_duplicate_full_text_user_eview_with_toggle_expand():
            review = reviews[0]

            def should_return_no_duplicate_full_text_user_review_with_toggle_expand():
                assert review['username'] == 'PonR.'
                assert review['full_text_of_review'] == "Singer was meant to finish directing the X-Men trilogy, and this proves it. The look of Superman Returns, while beautiful and streamlined, doesn't feel the way a Superman epic should. The lighting was never right and so everything looked dull and grey. The characters had little or no depth, with Superman showing no sign of anything resembling a personality and Lex Luthor's trademark cunning and meticulous scheming replaced with an over-the-top plan that carried no degree of subtlety or credibility. Overall, it was a good film, but not a great one. We could've had a great superhero film and it would've been X3. Instead we get two mediocre films marred forever by missed opportunities."

        def describe_no_duplicate_full_text_user_review_with_no_toggle_expand():
            review = reviews[12]

            def should_return_no_duplicate_full_text_review_with_toggle_expand():
                assert review['username'] == 'Matt'
                assert review['full_text_of_review'] =="One of the worst movies of the year for me. Dull, detached, and predictable to the last detail, Superman Returns fails miserably compared to other recent superhero films. The only positive note is Kevin Spacy's acceptable performance."

    def describe_no_duplicate_full_text_critic_review():
        resp = response_from("full critic reviews - Critic Reviews for Superman Returns - Metacritic.html", url="https://www.metacritic.com/movie/superman-returns/critic-reviews")
        resp.meta['review_page_number'] = 1
        resp.meta['movie_id'] = 'superman-returns'
        reviews = to_test.parse_movie_reviews(resp)


        def describe_no_duplicate_full_text_critic_review_with_toggle_expand():
            review = reviews[0]

            def should_return_no_duplicate_full_text_critic_review_with_toggle_expand():
                assert review['username'] == 'Richard Corliss'
                assert review['full_text_of_review'] == "The best Hollywood movies always knew how to sneak a beguiling subtext into a crowd-pleasing story. Superman Returns is in that grand tradition. That's why it's beyond Super. It's superb."

        def describe_no_duplicate_full_text_critic_review_with_no_toggle_expand():
            review = reviews[12]

            def should_return_no_duplicate_full_text_critic_review_with_toggle_expand():
                assert review['username'] == 'Joe Morgenstern'
                assert review['full_text_of_review'] =="The daunting logistics of Superman Returns have obviously affected the director's work -- thus the hit-or-miss continuity of the narrative -- but Bryan Singer hasn't been defeated by them. While his movie can be cumbersome, it's consistently alive, and that is saying a lot when many such productions are dead in the water, on land or in the air. Also, how can you resist the charm of a fantasy in which everyone gets his news from newspapers?"



        