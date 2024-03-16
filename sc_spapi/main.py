import csv
import datetime as dt
import logging
import os

from db.db_client import DBClient
from settings import SCRIPT_LOG_PATH, ACTIVE_EMAIL_NOTIFICATION
from sc_sales import SCSales


from script_notifier.monitor import ScriptStatusMonitor

class Reports:
    def __init__(self, ) -> None:
        db = DBClient()

    def download_sc_sales_report(self, country:str="US") -> None:
        vc_sales = SCSales(country=country)
        vc_sales.download_report()

def createLogPath(folder_name):
    
    log_path_dir = "\\".join([SCRIPT_LOG_PATH, folder_name])
    if not os.path.exists(log_path_dir):
        os.makedirs(log_path_dir)
    
    date_now = dt.datetime.now().date()
    filename = "_".join([folder_name, str(date_now)])
    filename = ".".join([filename, 'log'])
    log_path = "\\".join([log_path_dir, filename])
    return log_path

log_path = createLogPath('smartish-sc-spapi') 
logging.basicConfig(format='%(asctime)s:[%(levelname)s]:[%(filename)s][\"%(funcName)s()\"][line %(lineno)d]: %(message)s', filename=log_path, level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", force=True)

def report_status(script_name:str, status:str):
    monitor = ScriptStatusMonitor(script_name=script_name, status=status)
    monitor.save_to_log()

if __name__ == "__main__":
    logging.info("\n")
    logging.info("\"===========================SPAPI===========================\"")
    logging.info(f"log filename: {log_path}")
    logging.info(f"Saving log to {log_path}")
    print(f"Saving log to {log_path}")
    sc_spapi = Reports()
    
    try:
        sc_spapi.download_sc_sales_report(country="US")
        sales_status = "success"
    except Exception as e:
        logging.error(f"Failed to run successfully: {e}")
        sales_status = "fail"
    
    logging.info(f"Done running the smartish-sc-spapi script: {sales_status}")
    if ACTIVE_EMAIL_NOTIFICATION:
        report_status(script_name="SC-SPAPI: Sales", status=sales_status)