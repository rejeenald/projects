import logging
import subprocess
try:
    from op_sheet_settings import LABEL_MAKER_EXE
except:
    from .op_sheet_settings import LABEL_MAKER_EXE

class LabelMaker:
    def __init__(self, filename:str, order_ids:list) -> None:
        logging.info("===============LabelMaker===============")
        self.filename = filename.split("\\")[-1]
        self.order_ids = order_ids
        self.op_sheet_info = " ".join([self.filename] + self.order_ids)

    def execute_label_maker(self) -> None:
        logging.debug(f"Operator Sheet Information: {self.op_sheet_info}")
        print(f"Operator Sheet Information: {self.op_sheet_info}")
        args = [LABEL_MAKER_EXE, self.filename] + self.order_ids
        try:
            logging.info("Runing the subprocess for labels.exe...")
            subprocess.call(args, shell=True)
        except Exception as e:
            logging.error(f"Failed label maker (labels.exe): {e}")
        logging.info("Done with label maker!")