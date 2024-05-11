import logging
import psutil
import win32com

class CloseCustomupdaterFile:
    def __init__(self, filepath:str) -> None:
        logging.info("=============================CloseCustomupdaterFile=============================")
        self.file_path = filepath

    def safely_close(self) -> None:        
        try:
            excel = win32com.client.Dispatch("Excel.Application")
            workbook = excel.Workbooks.Open(self.file_path)
            workbook.Close(True)  # Save and close the workbook
            excel.Quit()
            logging.info(f"Excel file '{self.file_path}' was safely closed.")
        except Exception as e:
            logging.error(f"Failed to close custom updater file: {e}")
        

    def find_open_excel_file(self) -> str:
        psutil_process = psutil.process_iter(attrs=['pid', 'name'])
        logging.debug(f"process psutil: {psutil_process}")
        for process in psutil_process:
            try:
                process_name = process.info['name']
                process_pid = process.info['pid']

                if process_name == 'EXCEL.EXE':
                    for window in process.connections(kind='inet'):
                        if self.file_path in window.laddr and window.status == psutil.CONN_LISTEN:
                            return str(process_pid)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return None
