import logging
import openpyxl
import pandas as pd
pd.options.mode.chained_assignment = None
import psutil

import shutil


from openpyxl.styles import Border, Side
from time import sleep
from win32com import client


try:
    from .packing_slips import LabelMaker
    from .order_batches import OrderBatches
    from .op_sheet_settings import *
except:
    from packing_slips import LabelMaker
    from order_batches import OrderBatches
    from op_sheet_settings import *

class OpSheetGenerator:
    def __init__(self, artboard:pd.DataFrame, regular:bool) -> None:
        logging.info("===============OpSheetGenerator===============")
        self.batches = OrderBatches(artboard=artboard, regular=regular).batches
        self._item_ids_by_filename = {}

    @property
    def item_ids_by_filename(self) -> dict:
        return self._item_ids_by_filename
    
    def create_operator_sheets(self) -> None:
        logging.info(f"Expected op sheet count: {len(self.batches)}")
        for batch in self.batches:
            csv_filename = CSV_DIR + f"\{self.batches[batch]['filename'].unique()[0]}"
            logging.debug(f"CSV filename: {csv_filename}")
            if "ERROR" in csv_filename:
                logging.warning(f"Error in the CSV filename: {csv_filename}")
                continue
        
            filename = self._encode_orders_in_template(batch=self.batches[batch])
            if filename:
                self._batch_design_urls_to_csv(batch=self.batches[batch])
                logging.debug(f"batch: {self.batches[batch]}")
                self._item_ids_by_filename[filename] = list(self.batches[batch]["Order - ItemID"].unique())
                order_ids = list(self.batches[batch]["Order - ID"])
                self._attach_packing_slips(filename=filename, order_ids=order_ids)        
    
    def _encode_orders_in_template(self, batch:pd.DataFrame) -> None:
        logging.info("Encoding orders to template...")
        printer = batch["printer"].unique()[0]
        if printer == "6042":
            filename = self._encode_in_template(orders=batch, template=TEMPLATE_6042, template_table=TEMPLATE_6042_TABLE, printer=printer)          
        else:
            filename = self._encode_in_template(orders=batch, template=TEMPLATE_7151, template_table=TEMPLATE_7151_TABLE, printer=printer)
        
        try:
            self._export_to_pdf(filename=filename)
        except Exception as e:
            logging.warning(f"Failed to export to pdf.  Skipping this operator sheet.{filename} >>> {e}")
            return

        return filename

    def _encode_in_template(self, orders:pd.DataFrame, template:'openpyxl Worksheet', template_table:dict, printer:str) -> None:
        logging.info("Encoding to template...")
        op_sheet_excel = openpyxl.load_workbook(template, read_only=False)
        raw_data_sheet = op_sheet_excel['RAW DATA']

        op_sheet_top_left_detail = self.__get_op_sheet_top_left_detail(orders.iloc[:1].to_dict()["op_sheet_top_left_detail"])
        op_sheet_top_left_detail_cell = PRINT_SETTINGS_CELL

        try:
            logging.debug(f"op_sheet_top_left_detail: {op_sheet_top_left_detail}; {type(op_sheet_top_left_detail)}")
            raw_data_sheet[op_sheet_top_left_detail_cell].value = op_sheet_top_left_detail
        except Exception as e:
            logging.error(f"Failed to add top detail: {e}")


        for slot, cells in template_table.items():
            try:
                current_order = orders.iloc[slot-1].to_dict()
            except Exception as e:
                break

            raw_data_sheet[cells[0]].value = current_order["Order - Number"]
            raw_data_sheet[cells[1]].value = current_order["Ship To - Name"]
            raw_data_sheet[cells[2]].value = current_order["Sort Sku"]
            raw_data_sheet[cells[3]].value = current_order["Design"]
            raw_data_sheet[cells[4]].value = current_order["IS MULTI"]
            raw_data_sheet[cells[5]].value = CSV_DIR + current_order["FilePath"]

        
        filename = OP_SHEETS + current_order["filename"]
        logging.debug(f"_encode_in_template: {filename}")
        op_sheet_excel.save(filename + ".xlsx")
        return filename
    
    def __get_op_sheet_top_left_detail(self, op_sheet_top_left_detail) -> dict:
        for indx, val in op_sheet_top_left_detail.items():
            op_sheet_top_left_detail = op_sheet_top_left_detail[indx]
            break
        return op_sheet_top_left_detail
    
    def _batch_design_urls_to_csv(self, batch) -> None:
        logging.info("Saving the design urls to csv...")
        batch["URL"] = batch["FilePath"].apply(lambda design: PRODUCTION_SYNC + f"\\{design}")
        csv_filename = CSV_DIR + f"\{batch['filename'].unique()[0]}.csv"
        batch.to_csv(csv_filename, columns=["URL"], index=False)   

    def _export_to_pdf(self, filename:str) -> str:
        logging.info("Exporting the op_sheet csv to pdf version...")
        backup_op_sheet = filename.replace(OP_SHEETS, TEMPLATE_BACKUP) + ".xlsx"
        app = client.DispatchEx("Excel.Application")
        app.Interactive = False
        app.Visible = False
        op_sheet_excel = app.Workbooks.Open(filename + ".xlsx")
        op_sheet_excel.RefreshAll()
        op_sheet_excel.ActiveSheet.ExportAsFixedFormat(0, filename)
        op_sheet_excel.Save()
        op_sheet_excel.Close()
        shutil.move(filename + ".xlsx", backup_op_sheet)
        logging.info(f"Exported: {filename}")

    def _attach_packing_slips(self, filename:str, order_ids:list) -> None:
        logging.debug(f"order_ids: {order_ids}")
        logging.debug(f"filename: {filename}")
        lm = LabelMaker(filename=filename, order_ids=order_ids)
        lm.execute_label_maker()
        logging.debug(f"Attached packing slips of these order ids: {order_ids}")
        logging.info(f"Done attaching packing slips to operator sheet: {filename}")

        self._kill_illustrator()
        logging.info("Illustrator process is terminated!")

    def _kill_illustrator(self):
        sleep(5)
        logging.info(f"Terminating the Adobe Illustrator process...")
        try:
            self._terminate_illustrator()
        except Exception as e:
            logging.warning("Failed to terminate the Adobe Illustrator!")

        sleep(5)

    @staticmethod
    def _terminate_illustrator() -> None:
        logging.info("Killing Illustrator.exe process...")
        for process in psutil.process_iter():
            try:
                if "Illustrator.exe" in process.name():
                    process.kill()
            except Exception as e:
                logging.warning("Failed to kill the Adobe Illustrator!")
                pass

# if __name__ == "__main__":
#     s = OpSheetGenerator()
#     s.create_operator_sheets()