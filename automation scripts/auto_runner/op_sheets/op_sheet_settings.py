import pandas as pd
import string
import sys
sys.path.append("..")
from settings import SYNCPLICITY_ROOT, RESULTS_PATH, CSV_DIR, FILE, OLD_JOB_DIR, INV_FILE, OP_SHEET_SUFFIX, OP_SHEETS, PRODUCTION, TO_PRINT_ARTBOARD, BATCHES, ATTACH_PACKING_SLIPS

if PRODUCTION:
    TEMPLATE_6042 = RESULTS_PATH + "abAutomation6042_v2.xlsx"
    TEMPLATE_7151 = RESULTS_PATH + "abAutomation7151_v2.xlsx"
    TEMPLATE_BACKUP = RESULTS_PATH + "template_backups\\"
    ORDERS_CSV = RESULTS_PATH + "\\raw_data\\orders.csv"
else:
    TEMPLATE_6042 = RESULTS_PATH + "abAutomation6042_v2_test.xlsx"
    TEMPLATE_7151 = RESULTS_PATH + "abAutomation7151_v2_test.xlsx"
    TEMPLATE_BACKUP = RESULTS_PATH + "template_backups\\testing\\"
    ORDERS_CSV = RESULTS_PATH + "\\raw_data\\orders_test.csv"

OP_SHEETS = OP_SHEETS
OP_SHEET_SUFFIX = OP_SHEET_SUFFIX
LABEL_MAKER_FOLDER = RESULTS_PATH + "Exe Files to Run\\"
LABEL_MAKER_EXE = LABEL_MAKER_FOLDER + "labels.exe"
CUSTOM_UPDATER_FILE = FILE
PRODUCTION_SYNC = SYNCPLICITY_ROOT + "\\Production"
CSV_DIR = CSV_DIR
OLD_JOB_DIR = OLD_JOB_DIR
INV_FILE = INV_FILE

GROUPINGS_COLS = ["group_number", "family_sku", "printer"]
GROUPING_SHEET_NAME = "Group by FamSKU"
# ARTBOARD = ARTBOARD
SKU_GROUPINGS = pd.read_excel(CUSTOM_UPDATER_FILE, sheet_name=GROUPING_SHEET_NAME, usecols=GROUPINGS_COLS)
TEMPLATE_7151_TABLE = {slot: ["".join([column[1],str(slot+1)]) for column in enumerate(string.ascii_uppercase[1:7])] for slot in range(1,21)}
TEMPLATE_6042_TABLE = {slot: ["".join([column[1],str(slot+1)]) for column in enumerate(string.ascii_uppercase[1:7])] for slot in range(1,13)}
LIMIT_7151 = 20
LIMIT_6042 = 12

PRINT_SETTINGS_CELL = "B23"
TO_PRINT_ARTBOARD = TO_PRINT_ARTBOARD
BATCHES = BATCHES
ATTACH_PACKING_SLIPS = ATTACH_PACKING_SLIPS