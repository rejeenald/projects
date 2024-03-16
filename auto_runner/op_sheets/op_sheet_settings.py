import pandas as pd
import string
import sys
sys.path.append("..")
from settings import SYNCPLICITY_ROOT, RESULTS_PATH, CSV_DIR, FILE, OLD_JOB_DIR, INV_FILE, OP_SHEET_SUFFIX, OP_SHEETS, PRODUCTION, TO_PRINT_ARTBOARD, BATCHES

if PRODUCTION:
    TEMPLATE_6042 = RESULTS_PATH + "-----------------------------"
    TEMPLATE_7151 = RESULTS_PATH + "-----------------------------"
    TEMPLATE_BACKUP = RESULTS_PATH + "-----------------------------"
    ORDERS_CSV = RESULTS_PATH + "-----------------------------"
else:
    TEMPLATE_6042 = RESULTS_PATH + "-----------------------------"
    TEMPLATE_7151 = RESULTS_PATH + "-----------------------------"
    TEMPLATE_BACKUP = RESULTS_PATH + "-----------------------------"
    ORDERS_CSV = RESULTS_PATH + "-----------------------------"

OP_SHEETS = OP_SHEETS
OP_SHEET_SUFFIX = OP_SHEET_SUFFIX
LABEL_MAKER_FOLDER = RESULTS_PATH + "-----------------------------"
LABEL_MAKER_EXE = LABEL_MAKER_FOLDER + "-----------------------------"
CUSTOM_UPDATER_FILE = FILE
PRODUCTION_SYNC = SYNCPLICITY_ROOT + "-----------------------------"
CSV_DIR = CSV_DIR
OLD_JOB_DIR = OLD_JOB_DIR
INV_FILE = INV_FILE

GROUPINGS_COLS = ["-----------------------------"]
GROUPING_SHEET_NAME = "-----------------------------"
# ARTBOARD = ARTBOARD
SKU_GROUPINGS = pd.read_excel(CUSTOM_UPDATER_FILE, sheet_name=GROUPING_SHEET_NAME, usecols=GROUPINGS_COLS)
TEMPLATE_7151_TABLE = {slot: ["".join([column[1],str(slot+1)]) for column in enumerate(string.ascii_uppercase[1:7])] for slot in range(1,21)}
TEMPLATE_6042_TABLE = {slot: ["".join([column[1],str(slot+1)]) for column in enumerate(string.ascii_uppercase[1:7])] for slot in range(1,13)}
LIMIT_7151 = 20
LIMIT_6042 = 12

PRINT_SETTINGS_CELL = "-----------------------------"
TO_PRINT_ARTBOARD = TO_PRINT_ARTBOARD
BATCHES = BATCHES