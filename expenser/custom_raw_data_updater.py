import logging
import pandas as pd
import xlwings as xw

from settings import *

class CustomRawDataUpdater:
    def __init__(self, artboard:pd.DataFrame) -> None:
        logging.info("===============CustomRawDataUpdater===============")
        print("CustomRawDataUpdater")
        self.artboard = artboard

    def update_custom_updater_file_raw_data(self, item_ids:tuple) -> None:
        logging.info("Updating expense columns...")
        logging.debug(f"item ids: {item_ids}")
        app = xw.App()
        app.visible = False
        wb = xw.Book(FILE)
        ws = wb.sheets["Raw Data"]
        
        for order in self.artboard.iterrows():
            row = order[0] + 2
            item_id_cell = f"{ORDER_ITEM_ID_COL}{row}"
            print_cell = f"{PRINT_COL}{row}"
            expensed_cell = f"{EXPENSE_COL}{row}"
            
            item_id_from_cell = ws.range(item_id_cell).value
            
            if item_id_from_cell in item_ids:
                item_is_printed = ws.range(print_cell).value
                logging.info(f"{print_cell}: {item_is_printed}")
                if item_is_printed == "YES":
                    logging.info(f"item_id_from_cell: {item_id_from_cell}")
                    ws.range(expensed_cell).value = "YES"

        wb.save()
        wb.close()
        app.quit()
        logging.info("Done updating raw data Printed column!")

    