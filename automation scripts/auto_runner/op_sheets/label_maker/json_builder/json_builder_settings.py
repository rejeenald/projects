# from ..settings import SYNCPLICITY_ROOT, UPDATER_PATH, BUILD_DIR, SHIPSTATION_ACCESS


import os
from ssapi.api import ShipStation

PRODUCTION = True
TESTING = False

SYNCPLICITY_ROOT = os.getenv("SYNCPLICITY_HOME")
if PRODUCTION:
    UPDATER_PATH = SYNCPLICITY_ROOT + "\\Order Fulfillment\\Custom Orders\\Script Stuff\\"
else:
    UPDATER_PATH = SYNCPLICITY_ROOT + "\\Order Fulfillment\\Custom Orders\\FOR DEVELOPMENT AND TESTING\\"

OPERATOR_SHEET_DIR = UPDATER_PATH + "operator sheets"
TOOLS_DIR = UPDATER_PATH + 'Exe Files to Run'
BUILD_DIR = UPDATER_PATH + '_labels'
LABEL_DIR = BUILD_DIR + '\\labels'
BACKUP_LABEL_DIR = BUILD_DIR + '\\backup_labels'
SLIP_DIR = BUILD_DIR + '\\slips'
CONFIRMATION_FILES_DIR = BUILD_DIR + "\\confirmation files"

SHIPSTATION_KEY = os.getenv("SHIPSTATION_KEY")
SHIPSTATION_SECRET = os.getenv("SHIPSTATION_SECRET")
SHIPSTATION_ACCESS = ShipStation(auth_key=SHIPSTATION_KEY, auth_secret=SHIPSTATION_SECRET)



SHIPSTATION_ACCESS = SHIPSTATION_ACCESS

SYNCPLICITY_ROOT = SYNCPLICITY_ROOT
BUILD_DIR = BUILD_DIR
UNSHIPPED_ORDERS = UPDATER_PATH + r"\raw_data\orders.csv"
ORDERS_BACKUP = UPDATER_PATH + r"\raw_data\orders.bak.csv"
OTHER_ORDERS = UPDATER_PATH + r"\\raw_data\\other_orders\\"

UNVERIFIED_ORDERS = OTHER_ORDERS + r"\\unverified_unshipped_orders\\"
VERIFIED_ORDERS = OTHER_ORDERS + r"\\verified_unshipped_orders\\"

JSON_HEADERS = ["orderId", "orderNumber", "name", "address1", "address2", "status", "storeId", "items", "location", "date", "validated", "desc", "service_code"]