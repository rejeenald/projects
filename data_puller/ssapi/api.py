import requests

class RateLimitException(Exception):
    pass


class ShipStation:
    def __init__(self, auth_key=None, auth_secret=None, debug=False):
        if auth_key is None:
            raise AttributeError("Auth Key is required")
        if auth_secret is None:
            raise AttributeError("Auth Secret is required")

        else:
            self.__auth_key = auth_key
            self.__auth_secret = auth_secret

        self.__url = "https://ssapi.shipstation.com"
        self.__debug = debug
        self.__calls = 40
        self.__refresh = 0

    def __get(self, endpoint="", payload=None):
        url = f"{self.__url}{endpoint}"

        r = requests.get(url, auth=(self.__auth_key, self.__auth_secret), params=payload)
        if r.status_code == 429:
            raise RateLimitException(f"Too many requests! Rate Limited. Please Wait {self.__refresh}"
                                     f" seconds before another request")

        if self.__debug:
            print(r.headers)
            # print(r.json())

        self.__calls = int(r.headers['X-Rate-Limit-Remaining'])
        self.__refresh = int(r.headers['X-Rate-Limit-Reset'])

        # return r
        return r.json()

    def __post(self, endpoint="", payload=None):
        url = f"{self.__url}{endpoint}"
        r = requests.post(url, auth=(self.__auth_key, self.__auth_secret), json=payload)
        if r.status_code == 429:
            raise RateLimitException(f"Too many requests! Rate Limited. Please Wait {self.__refresh}"
                                     f" seconds before another request")

        if self.__debug:
            print(r.headers)
            print(r.status_code)
            print(r.json())

        self.__calls = int(r.headers['X-Rate-Limit-Remaining'])
        self.__refresh = int(r.headers['X-Rate-Limit-Reset'])

        # return r.json()

    def get_customer_list(self, state_code=None, country_code=None, marketplace_id=None,
                          tag_id=None, sort_by=None, sort_dir=None, page=None, page_size=None):
        payload = {
            'stateCode': state_code,
            'countryCode': country_code,
            'marketplaceId': marketplace_id,
            'tagId': tag_id,
            'sortBy': sort_by,
            'sortDir': sort_dir,
            'page': page,
            'pageSize': page_size
        }

        endpoint = "/customers"
        return self.__get(endpoint, payload)

    def get_customer_information(self, customer_id=None):
        if customer_id is None:
            raise AttributeError("Customer ID is required")
        else:
            endpoint = f"/customers/{customer_id}"
            return self.__get(endpoint)

    def get_stores(self):
        endpoint = "/stores"
        return self.__get(endpoint)

    def get_order_list(self, customer_name=None, item_keyword=None, create_date_start=None,
                       create_date_end=None, modify_date_start=None, modify_date_end=None,
                       order_date_start=None, order_date_end=None, shipby_date=None, order_number=None,
                       order_status=None, payment_date_start=None, payment_date_end=None,
                       store_id=None, sort_by=None, sort_dir=None, page=None, page_size=None):
        payload = {
            "customerName": customer_name,
            "itemKeyword": item_keyword,
            "createDateStart": create_date_start,
            "createDateEnd": create_date_end,
            "modifyDateStart": modify_date_start,
            "modifyDateEnd": modify_date_end,
            "orderDateStart": order_date_start,
            "orderDateEnd": order_date_end,
            "shipByDate": shipby_date,
            "orderNumber": order_number,
            "orderStatus": order_status,
            "paymentDateStart": payment_date_start,
            "paymentDateEnd": payment_date_end,
            "storeId": store_id,
            "sortBy": sort_by,
            "sortDir": sort_dir,
            "page": page,
            "pageSize": page_size
        }
        # print(f"payload: {payload}")
        endpoint = "/orders"
        return self.__get(endpoint, payload)

    def list_account_tags(self):
        endpoint = "/accounts/listtags"
        return self.__get(endpoint)

    def add_tag(self, order_id=None, tag_id=None):
        endpoint = "/orders/addtag"
        if not order_id or not tag_id:
            raise ValueError("order_id and tag_id are both required.")
        payload = {
            "orderId": order_id,
            "tagId": tag_id
        }
        self.__post(endpoint, payload)

    def create_label_for_order(self, order_id=None, carrier_code=None, service_code=None, confirmation=None,
                               ship_date=None, weight=None, dimensions=None, insurance_options=None,
                               international_options=None, advanced_options=None, test_label=False):
        endpoint = "/orders/createlabelfororder"
        payload = {
            "orderId": order_id,
            "carrierCode": carrier_code,
            "serviceCode": service_code,
            "confirmation": confirmation,
            "shipDate": ship_date,
            "weight": weight,
            "dimensions": dimensions,
            "insuranceOptions": insurance_options,
            "internationalOptions": international_options,
            "advancedOptions": advanced_options,
            "testLabel": test_label
        }

        # print(f"payload: {payload}")
        return self.__post(endpoint, payload)
