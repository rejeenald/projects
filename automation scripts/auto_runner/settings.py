import datetime as dt
import logging
import os
import pandas as pd
pd.options.mode.chained_assignment = None

PRODUCTION = True
PRODUCTION_EPS = True
OP_SHEETS_PRODUCTION = True
ARTBOARD_ONLY = True
ACTIVATE_EMAIL_NOTIFICATION = False

SYNCPLICITY_ROOT = os.getenv("SYNCPLICITY_HOME")
RESULTS_PATH = SYNCPLICITY_ROOT + "\\Order Fulfillment\\Custom Orders\\Script Stuff\\"

if PRODUCTION:
    CSV_DIR = RESULTS_PATH + "csv\\"
    FILE = RESULTS_PATH + "Custom Updater_v4.xlsm"
    BATCHES = RESULTS_PATH + "batches\\"
else:
    CSV_DIR = RESULTS_PATH + "\\csv\\testing\\"
    FILE = RESULTS_PATH + "Custom Updater Test.xlsm"
    BATCHES = RESULTS_PATH + "batches\\testing\\"

f = os.listdir(CSV_DIR)
if f:
    print(f"Found {len(f)} folders/files.")
    print(f)
logging.warning(f"No folders/files found: {len(f)}")


OP_SHEETS = RESULTS_PATH + "operator sheets\\"
REPORTS_PATHS = OP_SHEETS + "order_reports\\"
if OP_SHEETS_PRODUCTION:
    OP_SHEET_SUFFIX = "_AUTO_"
else:
    OP_SHEET_SUFFIX = "_TEST_"

OLD_JOB_DIR = CSV_DIR + "\\Old Jobs\\"
INV_FILE = RESULTS_PATH + r"inventory_levels.csv"
MODULE = "autoBots"
MACRO = "autoRun"

SWAP_NAMES = False
SKU_USERNAME = 'support@smartish.com'
SKU_PASS = 'Smartish1!'

# Custom Updater File
ORDER_ITEM_ID_COL = 'Y'
PRINT_COL = 'O'
EXPENSE_COL = 'P'
AB_FILE_COL = "AN"

def createLogPath(folder_name):
    SCRIPT_LOG_PATH = os.getenv('SCRIPT_LOG_FILES')
    log_path_dir = "\\".join([SCRIPT_LOG_PATH, folder_name])
    if not os.path.exists(log_path_dir):
        os.makedirs(log_path_dir)
    
    SCRIPT_LOG_PATH = os.getenv('SCRIPT_LOG_FILES')
    date_now = dt.datetime.now().date()
    filename = "_".join([folder_name, str(date_now)])
    filename = ".".join([filename, 'log'])
    log_path = "\\".join([log_path_dir, filename])
    return log_path

LOG_PATH = createLogPath('v6_cu_auto_runner')
logging.basicConfig(format='%(asctime)s:[%(levelname)s]:[%(filename)s][\"%(funcName)s()\"][line %(lineno)d]: %(message)s', filename=LOG_PATH, level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", force=True)
logging.info("====================================================================\n")
logging.info(f"Log filename: {LOG_PATH}")
print(f"Saving log to {LOG_PATH}")


ARTBOARD_COLS = ["Print Settings", "Table Height", "Trim", "Sort Sku", "Design", "Order - Number", "Ship To - Name", "FilePath", "IS MULTI", "Order - ItemID", "Order - ID", "Printed?", "Color", "Expensed", "Market - Marketplace Name"]
RAW_DATA_SHEET = "Raw Data"
ARTBOARD_ORIGINAL = pd.read_excel(FILE, sheet_name=RAW_DATA_SHEET, usecols=ARTBOARD_COLS)



####### Excluded Artboard #######
EXCLUDE_FROM_ARTBOARD = ARTBOARD_ORIGINAL.loc[(ARTBOARD_ORIGINAL["Order - ItemID"].notnull()) & (ARTBOARD_ORIGINAL["Design"].isna() | ARTBOARD_ORIGINAL["Color"].isna())]
EXCLUDE_FROM_ARTBOARD = ARTBOARD_ORIGINAL.loc[ARTBOARD_ORIGINAL["Design"].isin(["DESIGN NOT FOUND"]) | ARTBOARD_ORIGINAL["Trim"].isin(["AddToDesignPrintSettingsLookup"]) | ARTBOARD_ORIGINAL["Print Settings"].isin(["ADD2LOOKUP"])]
EXCLUDE_FROM_ARTBOARD_ORDER_NUMBERS = list(EXCLUDE_FROM_ARTBOARD["Order - Number"].unique())

date_time_now = dt.datetime.now(dt.timezone.utc).date()
date_time_str = date_time_now.strftime("%Y-%m-%d-%H-%M-%S")
EXCLUDE_PDF_FILEPATH = REPORTS_PATHS + "0-" + date_time_str + "-EXCLUDED_ORDERS_FOR_ISSUES.csv"
if EXCLUDE_FROM_ARTBOARD_ORDER_NUMBERS:
    EXCLUDE_FROM_ARTBOARD.to_csv(EXCLUDE_PDF_FILEPATH, index=False)

logging.info(f"Excluded orders from the processing: {len(EXCLUDE_FROM_ARTBOARD_ORDER_NUMBERS)}")
print(f"Excluded orders from the processing: {len(EXCLUDE_FROM_ARTBOARD_ORDER_NUMBERS)}")

TO_PRINT_PDF_FILEPATH = REPORTS_PATHS + "0-" + date_time_str + "-ON_OP_SHEETS_AND_ARTBOARDS.csv"
TO_PROCESS_ORDERS = ARTBOARD_ORIGINAL.loc[ARTBOARD_ORIGINAL["Order - ItemID"].notnull() & ARTBOARD_ORIGINAL["Design"] & ARTBOARD_ORIGINAL["Color"]]
TO_PRINT_ARTBOARD = TO_PROCESS_ORDERS[~TO_PROCESS_ORDERS["Printed?"].isin(["YES", "OOS"]) & ~TO_PROCESS_ORDERS["Expensed"].isin(["YES"])]
TO_PRINT_ARTBOARD = pd.merge(TO_PRINT_ARTBOARD, EXCLUDE_FROM_ARTBOARD, how="left", indicator=True).query("_merge=='left_only'").drop("_merge", axis=1)
TO_PRINT_ARTBOARD = TO_PRINT_ARTBOARD.sort_values(by="Sort Sku")


AMAZON_TO_PRINT_ARTBOARD = TO_PRINT_ARTBOARD[TO_PRINT_ARTBOARD["Market - Marketplace Name"].str.contains("Amazon Direct", na=False)]
print(AMAZON_TO_PRINT_ARTBOARD["Market - Marketplace Name"])
AMAZON_THRESHOLD_TO_SEPARATE = 1
print(len(AMAZON_TO_PRINT_ARTBOARD))
SEPARATE_AMAZON = False

if len(AMAZON_TO_PRINT_ARTBOARD) >= AMAZON_THRESHOLD_TO_SEPARATE:
    TO_PRINT_ARTBOARD = TO_PRINT_ARTBOARD[~TO_PRINT_ARTBOARD["Market - Marketplace Name"].str.contains("Amazon Direct", na=False)]
    AMAZON_TO_PRINT_PDF_FILEPATH = REPORTS_PATHS + "0-AMAZON-" + date_time_str + "-ON_OP_SHEETS_AND_ARTBOARDS.csv"
    AMAZON_TO_PRINT_ARTBOARD.to_csv(AMAZON_TO_PRINT_PDF_FILEPATH, index=False)
    SEPARATE_AMAZON = True

#  No longer contains any amazon orders
TO_PRINT_ARTBOARD.to_csv(TO_PRINT_PDF_FILEPATH, index=False)
ORDER_ITEMS_COUNT = len(ARTBOARD_ORIGINAL.loc[ARTBOARD_ORIGINAL["Order - ItemID"].notnull() & ARTBOARD_ORIGINAL["Design"] & ARTBOARD_ORIGINAL["Color"]])

OOS_REPORT_FILEPATH = REPORTS_PATHS + "0-" + date_time_str + "-IGNORED-FOR-OUT-OF-STOCK.csv"
OOS = TO_PROCESS_ORDERS[TO_PROCESS_ORDERS["Printed?"].isin(["OOS"])]
# print(OOS)
# print(ARTBOARD_ORIGINAL["Printed?"].isin("OOO"))
if not OOS.empty:
    print("Found OOS SKUs.")
    OOS.to_csv(OOS_REPORT_FILEPATH, index=False)
else:
    print("NO OOS SKUs.")

AB_FILE_DETAILS = ["Order - Number", "Order - ItemID", "Order - ID", "AB File"]
AB_FILE_DETAILS_FILEPATH = REPORTS_PATHS + "0-" + date_time_str + "-AB_FILE_DETAILS.csv"
AMAZON_AB_FILE_DETAILS_FILEPATH = REPORTS_PATHS + "0-AMAZON" + date_time_str + "-AB_FILE_DETAILS.csv"
MISSING_IMAGES_REPORT = REPORTS_PATHS + "0-" + date_time_str + "-MISSING_IMAGES_IN_ARTBOARDS.csv"