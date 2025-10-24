import datetime as dt
import logging
import os
import subprocess
from .label_maker.base.label_maker_executer import LabelMakerExecuter


class LabelMaker:
    def __init__(self, filename:str, order_ids:list) -> None:
        logging.info("===============LabelMaker===============")
        self.filename = filename
        self.order_ids = order_ids
        self.op_sheet_info = " ".join([self.filename] + self.order_ids)

    def execute_label_maker(self) -> None:
        logging.debug(f"Operator Sheet Information: {self.op_sheet_info}")
        print(f"Operator Sheet Information: {self.op_sheet_info}")
        args = [self.filename] + self.order_ids
        try:
            logging.info(f"Running the script for creating packing slips with these args: {args}")
            print(f"Running the script for creating packing slips with these args: {args}")
            lm = LabelMakerExecuter(sys_argv=args, run_in_console=False)
            lm.execute_label_maker()
        except Exception as e:
            logging.error(f"Failed label maker: {e}")
        logging.info("Done with label maker!")




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


log_path = createLogPath('v6_cu_label_maker') 
logging.basicConfig(format='%(asctime)s:[%(levelname)s]:[%(filename)s][\"%(funcName)s()\"][line %(lineno)d]: %(message)s', filename=log_path, level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", force=True)
    

# if __name__ == "__main__":

    
#     op_sheets = {
#         # "TEST_2025-06-27-07-11-42--6042--1200x1200-134-2-1142_AUTO_ - new": ['1305103193', '1304934068', '1305103462', '1305103470', '1305103463', '1305082763', '1305033233', '1305033317', '1304861492', '1304985535', '1304849538', '1305082771'],
#         "TEST_2025-07-04-11-07-39--6042--1200x1200-134-2-0739_AUTO_": ['1307303069']
#     }

#     for op_sheet_filename, order_ids in op_sheets.items():
#         print(f"filename: {op_sheet_filename} {order_ids}")
#         lm = LabelMaker(filename=op_sheet_filename, order_ids=order_ids)
#         lm.execute_label_maker()