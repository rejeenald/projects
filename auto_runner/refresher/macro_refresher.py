import logging
import os
from .remote_macro import RemoteMacro

class CustomUpdaterRefresher:
    def __init__(self, custom_updater:str) -> None:
        logging.info("===============CustomUpdaterRefresher===============")
        self.custom_updater = custom_updater

    def refresh_custom_updater(self) -> None:
        try:
            logging.info(f"Running {self.custom_updater} macro...")
            saver = RemoteMacro(excel_file=self.custom_updater)
        except Exception as e:
            logging.error(f"Erro accessing macro: {e}")
        
        try:
            saver.run_macro()
            logging.info(f"Done 'Refresh' of data for {self.custom_updater}.")
        except Exception as e:
            logging.error(f"Error running macro: {e}")

        saver.quit_excel()
        logging.info('Refreshing completed!')