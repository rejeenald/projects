import csv
import datetime as dt
import logging
import os

from db.db_client import DBClient
from settings import SCRIPT_LOG_PATH, ACTIVE_EMAIL_NOTIFICATION
from vc_forecasting import VCForecasting
from vc_inventory import VCInventory
from vc_sales import VCSales


from script_notifier.monitor import ScriptStatusMonitor

class Reports:
    def __init__(self, ) -> None:
        db = DBClient()

    def download_vc_sales_report(self, country:str="US") -> None:
        vc_sales = VCSales(country=country)
        vc_sales.download_report()

    def download_vc_inventory_report(self) -> None:
        vc_inventory = VCInventory()
        vc_inventory.download_report()

    def download_vc_forecasting_report(self) -> None:
        vc_forecasting = VCForecasting()
        vc_forecasting.download_report()



def createLogPath(folder_name):
    
    log_path_dir = "\\".join([SCRIPT_LOG_PATH, folder_name])
    if not os.path.exists(log_path_dir):
        os.makedirs(log_path_dir)
    
    date_now = dt.datetime.now().date()
    filename = "_".join(['smartish-spapi', str(date_now)])
    filename = ".".join([filename, 'log'])
    log_path = "\\".join([log_path_dir, filename])
    return log_path

log_path = createLogPath('smartish-spapi') 
logging.basicConfig(format='%(asctime)s:[%(levelname)s]:[%(filename)s][\"%(funcName)s()\"][line %(lineno)d]: %(message)s', filename=log_path, level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", force=True)

def report_status(script_name:str, status:str):
    monitor = ScriptStatusMonitor(script_name=script_name, status=status)
    monitor.save_to_log()

if __name__ == "__main__":
    logging.info("\n")
    logging.info("\"===========================SMARTISH-SPAPI===========================\"")
    logging.info(f"['smartish-spapi']: log filename: {log_path}")
    logging.info(f"Saving log to {log_path}")
    print(f"Saving log to {log_path}")
    vc_spapi = Reports()
    
    try:
        vc_spapi.download_vc_sales_report(country="CA")
        ca_sales_status = "success"
    except Exception as e:
        logging.error("Failed to run successfully: {e}")
        ca_sales_status = "fail"
    
    try:
        vc_spapi.download_vc_sales_report()
        us_sales_status = "success"
    except Exception as e:
        logging.error("Failed to run successfully: {e}")
        us_sales_status = "fail"
    
    try:
        vc_spapi.download_vc_inventory_report()
        us_inventory_status = "success"
    except Exception as e:
        logging.error(f"Failed to run successfully: {e}")
        us_inventory_status = "fail"

    try:
        vc_spapi.download_vc_forecasting_report()
        us_forecasting_status = "success"
    except Exception as e:
        logging.error("Failed to run successfully: {e}")
        us_forecasting_status = "fail"
    
    if ACTIVE_EMAIL_NOTIFICATION:
        report_status(script_name="VC-SPAPI: Canada sales", status=ca_sales_status)
        report_status(script_name="VC-SPAPI: US sales", status=us_sales_status)
        report_status(script_name="VC-SPAPI: US inventory", status=us_inventory_status)
        report_status(script_name="VC-SPAPI: US forecasting", status=us_forecasting_status)