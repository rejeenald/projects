import datetime as dt
import logging
import pandas as pd

from sc_reports import SCReports
from settings import MARKETPLACE_IDS

class SCSales(SCReports):
    def __init__(self, country:str, filename:str="sales_report") -> None:
        super().__init__(country=country)
        logging.info("\"===========================SCSales===========================\"")
        self.report_type = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"
        self.marketplace_id = MARKETPLACE_IDS[country]
        self.country = country
        self.report_data = None
        self.filename = filename

    def download_report(self) -> pd.DataFrame:
        logging.info(f"Downloading SC {self.country} Sales Report...")
        sales_report = self.request_report( marketplace_id=self.marketplace_id, report_type=self.report_type)
        sales_report = self._format_downloaded_report(sales_report=sales_report)
        # table_name = "_".join(["sales_seller_central", self.country])
        # sales_report.to_csv(f"{table_name}.csv", index=False)
        self.save_report_to_db(report=sales_report, table_name="sales_seller_central")

    def _format_downloaded_report(self, sales_report:pd.DataFrame) -> pd.DataFrame:
        logging.info(f"Fomatting downloaded sales report...")
        self.__remove_columns(sales_report)
        self.__rename_columns(sales_report)
        sales_report = self.__add_date_column(sales_report)
        logging.debug(f"sales report:\n:{sales_report}")
        return sales_report

    @staticmethod
    def __remove_columns(sales_report:pd.DataFrame) -> None:
        logging.info("Removing the following columns: 'url', 'customized_url', 'customized_page', 'customized_page', 'working', 'is_buyer_requested_cancellation'.")
        del sales_report["item-extensions-data"]
        del sales_report["is-business-order"]
        del sales_report["purchase-order-number"]
        del sales_report["price-designation"]
        del sales_report["signature-confirmation-recommended"]
        del sales_report["cpf"]

    @staticmethod
    def __rename_columns(sales_report:pd.DataFrame) -> None:
        sales_report.columns = [col.replace('-', '_') for col in sales_report.columns]

    def __add_date_column(self, sales_report:pd.DataFrame) -> None:
        logging.info(f"Inserting 'Date' column in the first column...")
        sales_report['Date'] = sales_report["purchase_date"]
        sales_report['Date'] = sales_report["Date"].apply(lambda x: self.__format_date_value__(x))
        return sales_report[["Date"] + [col for col in sales_report.columns if col != "Date"]]
    
    @staticmethod
    def __format_date_value__(date_value:str) -> str:
        date_value = date_value.split("+")[0]
        date_value = dt.datetime.strptime(date_value, "%Y-%m-%dT%H:%M:%S")
        return date_value.strftime("%m-%d-%Y")

