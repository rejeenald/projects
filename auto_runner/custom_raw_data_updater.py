import logging
import pandas as pd
import xlwings as xw

from settings import *

class CustomRawDataUpdater:
    def __init__(self) -> None:
        logging.info("===============CustomRawDataUpdater===============")
        print("CustomRawDataUpdater")

    def update_custom_updater_file_raw_data(self, item_ids_by_filename:dict) -> None:
        logging.info("update_custom_updater_file_raw_data")
        logging.debug(f"item ids: {item_ids_by_filename}")
        app = xw.App()
        app.visible = False
        wb = xw.Book(FILE)
        ws = wb.sheets["Raw Data"]
        

        for index in range(ORDER_ITEMS_COUNT):
            row = index + 2
            item_id_cell = f"{ORDER_ITEM_ID_COL}{row}"
            printed_cell = f"{PRINT_COL}{row}"
            ab_file_cell = f"{AB_FILE_COL}{row}"
            
            for ab_file, item_ids in item_ids_by_filename.items():
                ab_file = ab_file.split("\\")[-1]
                item_id_from_cell = ws.range(item_id_cell).value
                if str(item_id_from_cell) in item_ids:
                    print(f"item_id_from_cell: {item_id_from_cell}")
                    ws.range(printed_cell).value = "YES"
                    ws.range(ab_file_cell).value = ab_file

        wb.save()
        wb.close()
        app.quit()
        logging.info("Done updating raw data Printed column!")

    