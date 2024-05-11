import datetime as dt
import os
import pandas as pd

PRODUCTION = True
ACTIVATE_EMAIL_NOTIFICATION = True

SYNCPLICITY = os.getenv("SYNCPLICITY_HOME")
RESULTS_PATH = SYNCPLICITY + "------------------------"

if PRODUCTION:
    FILE = RESULTS_PATH + "Custom Updater_v4.xlsm"
    EXPENSE_FILE = SYNCPLICITY + r"------------------------.csv"
else:
    FILE = RESULTS_PATH + "------------------------.xlsm"
    EXPENSE_FILE = SYNCPLICITY + r"------------------------.csv"

EXPENSE_COL = 'P'
ORDER_ITEM_ID_COL = 'Y'
PRINT_COL = 'O'

LOG_PATH = SYNCPLICITY + r"------------------------"
LOG_FILE = LOG_PATH + "\\" + dt.date.today().strftime("%Y-%m-%d") + "-expense_log.log"

RAW_DATA_SHEET = "Raw Data"
ARTBOARD_ORIGINAL = pd.read_excel(FILE, sheet_name=RAW_DATA_SHEET)

####### Excluded Artboard #######
EXCLUDE_FROM_ARTBOARD = ARTBOARD_ORIGINAL.loc[(ARTBOARD_ORIGINAL["Order - ItemID"].notnull()) & (ARTBOARD_ORIGINAL["Design"].isna() | ARTBOARD_ORIGINAL["Color"].isna())]
EXCLUDE_FROM_ARTBOARD = ARTBOARD_ORIGINAL.loc[ARTBOARD_ORIGINAL["Design"].isin(["DESIGN NOT FOUND"]) | ARTBOARD_ORIGINAL["Trim"].isin(["AddToDesignPrintSettingsLookup"]) | ARTBOARD_ORIGINAL["Print Settings"].isin(["ADD2LOOKUP"])]

TO_PRINT_ARTBOARD = ARTBOARD_ORIGINAL.loc[ARTBOARD_ORIGINAL["Order - ItemID"].notnull() & ARTBOARD_ORIGINAL["Design"] & ARTBOARD_ORIGINAL["Color"]]
TO_PRINT_ARTBOARD = pd.merge(TO_PRINT_ARTBOARD, EXCLUDE_FROM_ARTBOARD, how="left", indicator=True).query("_merge=='left_only'").drop("_merge", axis=1)
ITEM_IDS_TO_EXPENSE = tuple(TO_PRINT_ARTBOARD["Order - ItemID"].unique())

TO_EXPENSE = ARTBOARD_ORIGINAL.loc[ARTBOARD_ORIGINAL["Printed?"].isin(["YES"]) & ~ARTBOARD_ORIGINAL["Expensed"].isin(["YES"])]
print(f"Initial To expense: {TO_EXPENSE}")
TO_EXPENSE.reset_index(drop=True, inplace=True)
TO_EXPENSE = TO_EXPENSE[~TO_EXPENSE["Custom SKU"].str.contains("FEATURED")]

print(f"Excluding featrueds: {TO_EXPENSE}")
ITEM_IDS_TO_EXPENSE = [str(int(item_id)) for item_id in tuple(TO_EXPENSE["Order - ItemID"].unique())]
print(f"ITEM_IDS_TO_EXPENSE: {ITEM_IDS_TO_EXPENSE}")
TO_EXPENSE_PIVOT_TABLE = TO_EXPENSE.groupby("Real Sku").size().reset_index(name='Count')
TO_EXPENSE_PIVOT_TABLE.to_csv(EXPENSE_FILE, index=False, header=False)