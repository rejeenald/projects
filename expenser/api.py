import logging
import requests
from time import sleep

ENDPOINT = 'https://app.skuvault.com/api/'
OFFICE_ID = "------------------------"
TEST_ID = "------------------------"
OFFICE_LOC = "OFFICE"
TEST_LOC = "TESTLOC"
SKU_IDX = 0
QTY_IDX = 1

class API:
    def __init__(self, tenant, user):

        # self.__user_email = cred[0]
        # self.__user_password = cred[1]

        self.__api = ENDPOINT
        self.__tenant_token = tenant
        self.__user_token = user

        # self.__authenticate()

    def __authenticate(self):
        tokens = 'getTokens'
        login = {"Email": self.__user_email, "Password": self.__user_password}
        resp = requests.post(ENDPOINT + tokens, json=login)

        if resp.status_code != 200:
            logging.critical("Unable to Authenticate! Exiting!")
            exit()
        else:
            data = resp.json()
            self.__tenant_token = data['TenantToken']
            self.__user_token = data['UserToken']

    def get_inventory(self):
        quantities = "inventory/getItemQuantities"
        start_date = None
        end_date = None
        page_number = 0
        page_size = 5000

        payload = {"ModifiedAfterDateTimeUtc": start_date,
                   "ModifiedBeforeDateTimeUtc": end_date,
                   "PageNumber": page_number,
                   "PageSize": page_size,
                   "ProductCodes": [],
                   "TenantToken": self.__tenant_token,
                   "UserToken": self.__user_token
                   }

        resp = requests.post(ENDPOINT + quantities, json=payload)

        while resp.status_code != 200:
            print("Response", resp.status_code)
            logging.warning("Quantities request failed!")
            resp = requests.post(ENDPOINT + quantities, json=payload)
            sleep(21)

        return resp.json()

    def get_warehouses(self, page_number = 0):
        warehouses = "inventory/getWarehouses"

        payload = {
            "PageNumber": page_number,
            "TenantToken": self.__tenant_token,
            "UserToken": self.__user_token
        }

        resp = requests.post(ENDPOINT + warehouses, json=payload)

        while resp.status_code != 200:
            print("Response", resp.status_code)
            logging.warning("Warehouses request failed!")
            resp = requests.post(ENDPOINT + warehouses, json=payload)
            sleep(61)

        return resp.json()

    def get_locations(self):
        locations = "inventory/getLocations"

        payload = {
            "TenantToken": self.__tenant_token,
            "UserToken": self.__user_token
        }

        resp = requests.post(ENDPOINT + locations, json=payload)

        while resp.status_code != 200:
            print("Response", resp.status_code)
            logging.warning("Locations request failed!")
            sleep(21)
            resp = requests.post(ENDPOINT + locations, json=payload)

        return resp.json()

    def remove_item_bulk(self, items):
        removals = []
        remove_items = "inventory/removeItemBulk"
        for item in items:
            # skip featured skus.  expensed straight from shipstation
            if "FEATURED" in item[SKU_IDX].upper():
                continue
            item_out = {
                "Sku": item[SKU_IDX],
                "WarehouseId": OFFICE_ID,
                "LocationCode": OFFICE_LOC,
                "Quantity": item[QTY_IDX],
                "Reason": "Custom printing",

            }
            removals.append(item_out)

        payload = {
            "Items": removals,
            "TenantToken": self.__tenant_token,
            "UserToken": self.__user_token
        }

        resp = requests.post(ENDPOINT + remove_items, json=payload)

        while resp.status_code > 400:
            print("Response: ", resp.status_code)
            logging.warning("Removal request failed!")
            sleep(21)
            resp = requests.post(ENDPOINT + remove_items, json=payload)

        print(resp)
        print(resp.text)
        return resp.json()
