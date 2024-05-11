import datetime as dt
import logging 
import os
from script_notifier.monitor import ScriptStatusMonitor
from settings import ACTIVE_EMAIL_NOTIFICATION, SCRIPT_LOG_PATH
from sc_cvr import SCCVR

def createLogPath(folder_name):
    
    log_path_dir = "\\".join([SCRIPT_LOG_PATH, folder_name])
    if not os.path.exists(log_path_dir):
        os.makedirs(log_path_dir)
    
    date_now = dt.datetime.now().date()
    filename = "_".join(['smartish-sc-spapi-cvr', str(date_now)])
    filename = ".".join([filename, 'log'])
    log_path = "\\".join([log_path_dir, filename])
    return log_path

log_path = createLogPath('smartish-spapi-cvr') 
logging.basicConfig(format='%(asctime)s:[%(levelname)s]:[%(filename)s][\"%(funcName)s()\"][line %(lineno)d]: %(message)s', filename=log_path, level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", force=True)

def report_status(script_name:str, status:str):
    monitor = ScriptStatusMonitor(script_name=script_name, status=status)
    monitor.save_to_log()

if __name__ == "__main__":
    logging.info("\n")
    logging.info("\"===========================SMARTISH-SPAPI===========================\"")
    logging.info(f"['smartish-spapi-cvr']: log filename: {log_path}")
    logging.info(f"Saving log to {log_path}")
    print(f"Saving log to {log_path}")
    cvr = SCCVR(country="US")
    
    try:
        cvr.download_cvr_report()
        sales_status = "success"
    except Exception as e:
        logging.error(f"Failed to run successfully: {e}")
        sales_status = "fail"

    logging.info(f"Done running the smartish-sc-spapi script: {sales_status}")
    if ACTIVE_EMAIL_NOTIFICATION:
        report_status(script_name="SC-SPAPI: Sales", status=sales_status)
        # report_status(script_name="VC-SPAPI: US sales", status=us_sales_status)
        # report_status(script_name="VC-SPAPI: US inventory", status=us_inventory_status)
        # report_status(script_name="VC-SPAPI: US forecasting", status=us_forecasting_status)