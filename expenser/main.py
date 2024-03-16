import logging
import sys
import os
import configparser
import csv
import argparse
import api
import datetime as dt

from time import sleep

from close_custom_updater_file import CloseCustomupdaterFile
from custom_raw_data_updater import CustomRawDataUpdater
from settings import EXPENSE_FILE, LOG_FILE, TO_PRINT_ARTBOARD, ITEM_IDS_TO_EXPENSE, FILE, TO_EXPENSE_PIVOT_TABLE

parser = argparse.ArgumentParser()
parser.add_argument ('-f', '--file', help="CSV file of items to be checked.")

args = parser.parse_args()

def main():
    logging.info("Updating inventory on SKUVault...")
    tenant = "bf5RtdevpeNcAFHOhGwUDyBC0E0q+EvWMMikpqqgTRY="
    user = "L584sQfqdn868rIHYxk7TzjUbUuLNcZet6vYby7KbOE="

    skuvault = api.API(tenant, user)
    logging.info(f"sku vault: {skuvault}")

    if _has_skus_to_expense():
        _expense_in_skuvault(skuvault)
        _safely_close_custom_updater_file_whenever_open()
        sleep(5)
        _mark_sku_with_yes()

def _has_skus_to_expense() -> None:
    logging.debug(len(TO_EXPENSE_PIVOT_TABLE))
    if len(TO_EXPENSE_PIVOT_TABLE) < 1:
        logging.warning("No SKUs to expense. Please double-check Custom updater file.")
        return
    else:
        logging.info(f"Found SKUs to expense: {TO_EXPENSE_PIVOT_TABLE}")
        return True

def _expense_in_skuvault(skuvault):
    try:
        __update_skuvault_inventory(skuvault)
    except TypeError as e:
        logging.fatal(400)
        logging.fatal("Type Error! Inventory Unchanged.")
        logging.fatal(e)
        sys.exit(1)
    except FileNotFoundError as e:
        logging.fatal(401)
        logging.fatal("File not found! Inventory Unchanged")
        logging.fatal(f"Exception error message: {e}")

def _safely_close_custom_updater_file_whenever_open() -> None:
    custom_updater = CloseCustomupdaterFile(filepath=FILE)
    process_id = custom_updater.find_open_excel_file()

    if process_id:
        custom_updater.safely_close()
    else:
        logging.info(f"Custom updater file NOT currently opened.")

def __update_skuvault_inventory(skuvault):
    with open(EXPENSE_FILE) as f:
        items = list(csv.reader(f))
        responses = skuvault.remove_item_bulk(items)
        logging.info(f"response: {responses}")
        error_flag = __record_error_count__(items, responses)
    if error_flag == 1:
        logging.fatal("Some SKUs were not updated in SkuVault. Please check the generated error log to manually "
                          f"update these Skus\n\n{LOG_FILE}")

def __record_error_count__(items, responses):
    error_flag = 0
    for i, response in enumerate(responses["Results"]):
        if response != "Success":
            with open(LOG_FILE, 'a') as g:
                logging.fatal(f"SKU: {items[i][0]}, QTY: {items[i][1]}\n")
                g.write(f"SKU: {items[i][0]}, QTY: {items[i][1]}\n")
            error_flag = 1
    return error_flag     

def _mark_sku_with_yes():
    custom_raw_data_updater = CustomRawDataUpdater(artboard=TO_PRINT_ARTBOARD)
    logging.info("Updating the custom updater file...")
    custom_raw_data_updater.update_custom_updater_file_raw_data(item_ids=ITEM_IDS_TO_EXPENSE)
    logging.info("Done making artboards!")


def createLogPath(folder_name):
    SCRIPT_LOG_PATH = os.getenv('SCRIPT_LOG_FILES')
    log_path_dir = "\\".join([SCRIPT_LOG_PATH, folder_name])
    if not os.path.exists(log_path_dir):
        os.makedirs(log_path_dir)
    
    SCRIPT_LOG_PATH = os.getenv('SCRIPT_LOG_FILES')
    date_now = dt.datetime.now().date()
    filename = "_".join(['expenser', str(date_now)])
    filename = ".".join([filename, 'log'])
    log_path = "\\".join([log_path_dir, filename])
    return log_path

if __name__ == "__main__":
    log_path = createLogPath('expenser')
    logging.basicConfig(format='%(asctime)s:[%(levelname)s]:[%(filename)s][\"%(funcName)s()\"][line %(lineno)d]: %(message)s', filename=log_path, level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", force=True)
    logging.info("\n")
    logging.info(f"[expenser]: log filename: {log_path}")
    print(f"Saving log to {log_path}")
    main()
    logging.info("Done running expenser.\n\n")