import datetime as dt
import logging
import os
from ss_order_puller import SSDataPuller
from time import sleep

from script_notifier.monitor import ScriptStatusMonitor
from script_notifier.status_reader import NotifyToEmail
from settings import ACTIVATE_EMAIL_NOTIFICATION

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

if __name__ == "__main__":
    log_path = createLogPath('data_puller')
    logging.basicConfig(format='%(asctime)s:[%(levelname)s]:[%(filename)s][\"%(funcName)s()\"][line %(lineno)d]: %(message)s', filename=log_path, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", force=True)

    logging.info(f"log filename: {log_path}")
    print(f"Saving log to {log_path}")


    try:
        d_puller = SSDataPuller()
        d_puller.save_to_csv_ss_data()
        status = "success"
    except Exception as e:
        logging.error(f"Failed to run successfully data_puller: {e}")
        status = "fail"
    monitor = ScriptStatusMonitor(script_name="data_puller", status=status)
    monitor.save_to_log()

    if ACTIVATE_EMAIL_NOTIFICATION:
        NotifyToEmail()
        logging.info("Done running data puller.\n\n")