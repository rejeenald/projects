from scrapy.utils.test import get_crawler
from scrapy_tdd import *
import pytest
from .myip_ms import MyipMsSpider

import os, logging, pkg_resources

def response_from(file_name, url="https://myip.ms/", meta=None):
    return mock_response_from_sample_file(my_path(__file__) + "/samples", file_name, url=url, meta=meta)


def describe_profile_spider():
    to_test = MyipMsSpider.from_crawler(get_crawler())

    

    def describe_ips_on_a_page():
        resp = response_from("page_1.html", url="https://myip.ms/browse/sites/1/own/376714")
        
        def describe_last_page_number():
            last_page_number = to_test._get_last_page_number(resp)

            def should_return_last_page_number():
                assert last_page_number == '4027'

        def describe_extracted_data():
            results = to_test.parse_page_data(resp)
            # print(results)

            def should_return_number_of_rows_in_page_1():
                assert len(results) == 50

            def describe_1st_row_data():
                first_row_results = results[0]

                def should_return_page_source_url():
                    assert first_row_results['src'] == 'https://myip.ms/browse/sites/1/own/376714'

                def should_item_data_visible_in_row():
                    assert first_row_results['number'] == '1'
                    assert first_row_results['website'] =='myshopify.com'
                    assert first_row_results['website_ip_address'] == '23.227.38.64'
                    assert first_row_results['web_hosting_company_or_IP_owner'] == 'Shopify, Inc'
                    assert first_row_results['web_hosting_or_server_IP_location'] == 'Canada'
                    assert first_row_results['web_hosting_city'] == 'Ottawa'
                    assert first_row_results['world_site_popular_rating'] == '# 43'

                def should_item_data_toggle_row():
                    assert first_row_results['website_popularity'] == '8,500,000 visitors per day'
                    assert first_row_results['IP_reverse_dns_host'] =='shops.myshopify.com'
                    assert first_row_results['top_level_hostname'] == 'myshopify.com'
                    assert first_row_results['web_hosting_state'] == 'Ontario'
                    assert first_row_results['dns_records'] == ['dns1.p06.nsone.net', 'ns3.dnsimple.com', 'ns4.dnsimple.com']
                    assert first_row_results['record_update_time'] == '02 May 2020, 00:14'

            def describe_25th_row_data():
                twentieth_row_results = results[24]

                def should_return_page_source_url():
                    assert twentieth_row_results['src'] == 'https://myip.ms/browse/sites/1/own/376714'

                def should_item_data_visible_in_row():
                    assert twentieth_row_results['number'] == '25'
                    assert twentieth_row_results['website'] =='skims.com'
                    assert twentieth_row_results['website_ip_address'] == '23.227.38.32'
                    assert twentieth_row_results['web_hosting_company_or_IP_owner'] == 'Shopify, Inc'
                    assert twentieth_row_results['web_hosting_or_server_IP_location'] == 'Canada'
                    assert twentieth_row_results['web_hosting_city'] == 'Ottawa'
                    assert twentieth_row_results['world_site_popular_rating'] == '# 8,367'

                def should_item_data_toggle_row():
                    # IP_reverse_dns_host is not available
                    assert twentieth_row_results['website_popularity'] == '29,900 visitors per day'
                    assert twentieth_row_results['IP_reverse_dns_host'] =='23.227.38.32'
                    assert twentieth_row_results['web_hosting_state'] == 'Ontario'
                    assert twentieth_row_results['dns_records'] == ['lynn.ns.cloudflare.com', 'rafe.ns.cloudflare.com']
                    assert twentieth_row_results['record_update_time'] == '02 May 2020, 00:18'
                
            