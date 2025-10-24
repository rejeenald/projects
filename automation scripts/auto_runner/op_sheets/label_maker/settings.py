import os
from ssapi.api import ShipStation

PRODUCTION = True
TESTING = False

SYNCPLICITY_ROOT = os.getenv("SYNCPLICITY_HOME")
if PRODUCTION:
    UPDATER_PATH = SYNCPLICITY_ROOT + "\\Order Fulfillment\\Custom Orders\\Script Stuff\\"
else:
    UPDATER_PATH = SYNCPLICITY_ROOT + "\\Order Fulfillment\\Custom Orders\\FOR DEVELOPMENT AND TESTING\\"

OPERATOR_SHEET_DIR = UPDATER_PATH + "\\operator sheets\\"
TOOLS_DIR = UPDATER_PATH + 'Exe Files to Run'
BUILD_DIR = UPDATER_PATH + '_labels'
LABEL_DIR = BUILD_DIR + '\\labels'
BACKUP_LABEL_DIR = BUILD_DIR + '\\backup_labels'
SLIP_DIR = BUILD_DIR + '\\slips'
CONFIRMATION_FILES_DIR = BUILD_DIR + "\\confirmation files"

SHIPSTATION_KEY = os.getenv("SHIPSTATION_KEY")
SHIPSTATION_SECRET = os.getenv("SHIPSTATION_SECRET")
SHIPSTATION_ACCESS = ShipStation(auth_key=SHIPSTATION_KEY, auth_secret=SHIPSTATION_SECRET)