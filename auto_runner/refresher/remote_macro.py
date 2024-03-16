from distutils.log import INFO
import os, os.path
import datetime as dt
import win32com.client
from time import sleep

import logging

class RemoteMacro:
    def __init__(self, excel_file, module = 'modAbAutomation',  macro = 'Workbook_RefreshALL'):
        self.excel_file = excel_file
        self.module = module
        self.macro = macro  
    

    def run_macro(self):
        logging.debug(f"['remote_macro - run_macro']: Excel file: {self.excel_file}")
        if os.path.exists(self.excel_file):
            # xl = win32com.client.Dispatch("Excel.Application")
            logging.debug(f"['remote_macro - run_macro']: Initiating runnign of macro")
            xl = win32com.client.gencache.EnsureDispatch("Excel.Application")
            logging.debug(f"['remote_macro - run_macro']: x1: {xl}")
            # xl.Interactive = False
            xl.Visible = True
            wb = xl.Workbooks.Open(os.path.abspath(self.excel_file))
            file_name = self.excel_file.split('\\')[-1]
            if len(file_name) == 1:
                print('file name not split -  use backslashes')
                logging.debug(f"['remote_macro - run_macro']: file name not split -  use backslashes")
                return

            print(file_name)
            logging.debug(f"['remote_macro - run_macro']: filename: {file_name}")
            full_macro_name = "'{}'!{}.{}".format(file_name, self.module, self.macro)
            logging.debug(f"['remote_macro - run_macro']: full_macro_name: {full_macro_name}")
            # xl.Application.Run("excelsheet.xlsm!modulename.macroname")
            xl.Application.Run(full_macro_name)
            logging.debug(f"['remote_macro - run_macro']: Closing macro.")
            # if you want to save then uncomment this line and change delete the ", ReadOnly=1" part from the open function.
            # xl.Application.SaveAs(os.path.abspath(self.excel_file))
            sleep(5)
            wb.Close(True)
            # xl.Application.Quit()  # Comment this out if your excel script closes
            sleep(5)
            logging.debug(f"['remote_macro - run_macro']: removing x1.")
            del xl
        else:
            logging.error(f"['remote_macro - run_macro']: Excel file not found: {self.excel_file}")
            print(self.excel_file)
            print('Excel file not found :(')

    def quit_excel(self):
        logging.debug(f"['remote_macro - quit_excel']: Quiting Excel")
        xl = win32com.client.gencache.EnsureDispatch("Excel.Application")
        xl.Application.Quit()
        logging.debug(f"['remote_macro - quit_excel']: Excel terminated!")