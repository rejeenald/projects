import datetime as dt
import logging
import os
import pandas as pd
from time import sleep
from artboard_processor import ArtboardProcessor
from settings import AMAZON_TO_PRINT_ARTBOARD, ACTIVATE_EMAIL_NOTIFICATION, AB_FILE_DETAILS, FILE, RAW_DATA_SHEET, AMAZON_AB_FILE_DETAILS_FILEPATH, SEPARATE_AMAZON, AMAZON_THRESHOLD_TO_SEPARATE
from script_notifier.monitor import ScriptStatusMonitor
from script_notifier.status_reader import NotifyToEmail


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

LOG_PATH = createLogPath('v6_cu_runner_artboard_only')
logging.basicConfig(format='%(asctime)s:[%(levelname)s]:[%(filename)s][\"%(funcName)s()\"][line %(lineno)d]: %(message)s', filename=LOG_PATH, level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", force=True)
logging.info("====================================================================\n")
logging.info(f"Log filename: {LOG_PATH}")
print(f"Saving log to {LOG_PATH}")

if __name__ == "__main__":
    if SEPARATE_AMAZON:
        artboard_processor = ArtboardProcessor(to_print_artboard=AMAZON_TO_PRINT_ARTBOARD)

        try:
            logging.info("Processing amazon orders....")
            artboard_processor.process_amazon_artboard()
            status = "success"
        except Exception as e:
            logging.error(f"Failed to run successfully process amazon orders artboard: {e}")
            status = "fail"

        monitor = ScriptStatusMonitor(script_name="amazon artboard", status=status)
        monitor.save_to_log()
        sleep(5)

        try:
            orders = pd.read_excel(FILE, sheet_name=RAW_DATA_SHEET, usecols=AB_FILE_DETAILS)
            orders.to_csv(AMAZON_AB_FILE_DETAILS_FILEPATH, index=False)
        except Exception as e:
            logging.error(f"Failed to save AB File details!")

    else:
        logging.info(f"Amazon Artboards less than the threshold: {AMAZON_THRESHOLD_TO_SEPARATE}")

    if ACTIVATE_EMAIL_NOTIFICATION:
        NotifyToEmail()
        print("Done running custom updater auto runner for amazon orders.")
        logging.info("Done running custom updater auto runner for amazon orders.\n\n")