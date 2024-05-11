import datetime as dt
from collections import ChainMap
import os
import pandas as pd

PRODUCTION = True
PRODUCTION_DATA = True
RAW_DATA = True
ACTIVATE_EMAIL_NOTIFICATION = True

HOURS_THRESHOLD = 720
START_TIME = dt.datetime.now() - dt.timedelta(hours=HOURS_THRESHOLD)

MAX_PAGE_SIZE = 500

SHIPSTATION_KEY = os.getenv("SHIPSTATION_KEY")
SHIPSTATION_SECRET = os.getenv("SHIPSTATION_SECRET")
PRINT_QUEUE_TAG = 117508

ZSKU_LOOKUP = {
    "iphone 11 pro max": "19P",
    "iphone 11 pro": "19",
    "iphone 11": "19M",
    "iphone 6 plus": "6P",
    "iphone 7": "7",
    "iphone 7 plus": "7P",
    "iphone xr": "XM",
    "iphone xs max": "XP"
}

SYNCPLICITY_ROOT = os.getenv("SYNCPLICITY_HOME")
MAX_PAGE_SIZE = 500

if PRODUCTION:
    RESULTS_DIR = SYNCPLICITY_ROOT + r"--------------------------------"
else:
    RESULTS_DIR = SYNCPLICITY_ROOT + "--------------------------------"

if RAW_DATA:
    ORDERS = RESULTS_DIR + r"--------------------------------.csv"
    ORDERS_BACKUP = RESULTS_DIR + r"--------------------------------.bak.csv"
    OTHER_ORDERS = RESULTS_DIR + r"--------------------------------"
    SHIPPED_ORDERS = OTHER_ORDERS + "_".join(["orders_shipped", ".csv"])
    CANCELLED_ORDERS = OTHER_ORDERS + "_".join(["orders_cancelled", ".csv"])
    TEST_ORDERS = OTHER_ORDERS + "_".join(["orders_test", ".csv"])
    PERSY_ORDERS = OTHER_ORDERS + "_".join(["--------------------------------", ".csv"])
    HISTORICAL_RECORDS_SHIPPED_ORDERS = RESULTS_DIR + r"--------------------------------.csv"
    HISTORICAL_RECORDS_CANCELED_ORDERS = RESULTS_DIR + r"--------------------------------.csv"
else:
    ORDERS = RESULTS_DIR + r"--------------------------------.csv"
    ORDERS_BACKUP = RESULTS_DIR + r"--------------------------------.bak.csv"
    OTHER_ORDERS = RESULTS_DIR + r"--------------------------------"
    SHIPPED_ORDERS = OTHER_ORDERS + "_".join(["orders_shipped", ".csv"])
    CANCELLED_ORDERS = OTHER_ORDERS + "_".join(["orders_cancelled", ".csv"])
    TEST_ORDERS = OTHER_ORDERS + "_".join(["orders_test", ".csv"])
    PERSY_ORDERS = OTHER_ORDERS + "_".join(["--------------------------------", ".csv"])
    HISTORICAL_RECORDS_SHIPPED_ORDERS = RESULTS_DIR + r"--------------------------------.csv"
    HISTORICAL_RECORDS_CANCELED_ORDERS = RESULTS_DIR + r"--------------------------------.csv"

OUTLIER = ["WOOD", "FLORAL", "MEOW", "ATARI", "LIMETIME", "DESERT", "PAWPRINTS", "DREAMCATCHER", "INBLOOM", "FULLBLOOM"]
PRINT_QUEUE_TAG = 117508
DATE_NOW = dt.datetime.now().date()

HEADERS = ["orderId", "orderNumber", "createDate", "orderDate", "modifyDate", "shipByDate", "customerId", "customerEmail",
           "orderTotal", "orderStatus", "name", "street1", "street2", "city", "state", "postalCode", "country", "phone",
           "store", "sku", "color", "design", "desc", "customizedURL", "itemId", "address_verified", "service_code", "item_sku_count"]

RAW_DATA_HEADERS = ['orderId', 'orderNumber', 'orderKey', 'orderDate', 'orderStatus', 'customerEmail', 'itemId', 'sku', 'item_count']
SKU_DEFAULT_COLORS = RESULTS_DIR + r"--------------------------------.xlsx"
SKU_COLOR_LOOKUP = pd.read_excel(SKU_DEFAULT_COLORS, index_col="SKU").to_dict().get("COLOR")

SHIPBYS = False
if SHIPBYS:
    SHIPBY_DATE = dt.datetime.now().date()
else:
    SHIPBY_DATE = None

DELAY_THRESHOLD = 20