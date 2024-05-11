import datetime as dt
import logging
import pandas as pd

from vc_reports import VCReports
from settings import MARKETPLACE_IDS, ASIN_SKU, INV_COLS

class VCInventory(VCReports):
    def __init__(self, country:str="US", filename:str="inventory_report") -> None:
        super().__init__()
        self.report_type = "GET_VENDOR_INVENTORY_REPORT"
        self.marketplace_id = MARKETPLACE_IDS[country]
        self.country = country
        self.report_data = None
        self.filename = filename

    def download_report(self) -> pd.DataFrame:
        logging.info(f"Downloading VC {self.country} Inventory Report...")
        report_data = self.request_report(marketplace_id=self.marketplace_id, report_type=self.report_type)
        # logging.info(f"VC inventory: {report_data}")
        inventory_report = pd.DataFrame.from_records(report_data["inventoryByAsin"])
        inventory_report = self._format_downloaded_report(inventory_report=inventory_report)
        # self._save_inventory_report(inventory_report=inventory_report)
        table_name = "_".join(["inv_vendor_central", self.country])
        self.save_report_to_db(report=inventory_report, table_name=table_name)

    def _format_downloaded_report(self, inventory_report:pd.DataFrame) -> pd.DataFrame:
        logging.info(f"Fomatting downloaded inventory report...")
        inventory_report.rename(columns = {'startDate':'Date', "asin": "ASIN", "sellableOnHandInventoryUnits": "Quantity"}, inplace = True)
        inventory_report["Quantity"] = inventory_report["Quantity"].apply(lambda q: self.__convert_to_int(q))
        inventory_report = self.__match_asin_sku(inventory_report=inventory_report)
        logging.debug(f"Matching done: {inventory_report.head()}")
        inventory_report = self.__remove_columns(inventory_report=inventory_report)
        logging.debug(f"Removed columns done: {inventory_report.head()}")
        return inventory_report
    
    @staticmethod
    def __convert_to_int(qty) -> int:
        try:
            return int(qty)
        except ValueError as e:
            logging.warning(f"QTY values is not a number: {qty}")
            return 0
        except Exception as e:
            logging.warning(f"Cannot identify issue: {e}")
            return 0
    
    @staticmethod
    def __match_asin_sku(inventory_report:pd.DataFrame) -> str:
        logging.info("Matching asin sku...")
        asin_sku = pd.read_csv(ASIN_SKU)
        try:
            logging.debug(f"Inventory report to merge: {inventory_report}")
            inventory_report = inventory_report.merge(right=asin_sku, how="left", on=["ASIN"], validate="many_to_one")
            logging.debug(f"Inventory report merged with SKU: {inventory_report}")
        except Exception as e:
            logging.error(f"Cannot merge: {e}")
        return inventory_report


    @staticmethod
    def __remove_columns(inventory_report:pd.DataFrame) -> None:
        logging.info(f"Retaining inventory columns only: {INV_COLS}")
        return inventory_report[INV_COLS]