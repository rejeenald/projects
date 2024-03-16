import datetime as dt
import logging
import pandas as pd

from vc_reports import VCReports
from settings import MARKETPLACE_IDS

class VCSales(VCReports):
    def __init__(self, country:str, filename:str="sales_report") -> None:
        super().__init__(country=country)
        logging.info("\"===========================VCSales===========================\"")
        self.report_type = "GET_VENDOR_SALES_REPORT"
        self.marketplace_id = MARKETPLACE_IDS[country]
        self.country = country
        self.report_data = None
        self.filename = filename

    def download_report(self) -> pd.DataFrame:
        logging.info(f"Downloading VC {self.country} Sales Report...")
        report_data = self.request_report( marketplace_id=self.marketplace_id, report_type=self.report_type)
        sales_report = pd.DataFrame.from_records(report_data["salesByAsin"])
        sales_report = self._format_downloaded_report(sales_report=sales_report)
        table_name = "_".join(["sales_vendor_central", self.country])
        self.save_report_to_db(report=sales_report, table_name=table_name)

    def _format_downloaded_report(self, sales_report:pd.DataFrame) -> pd.DataFrame:
        logging.info(f"Fomatting downloaded sales report...")
        sales_report.rename(columns = {'startDate':'Date', "asin": "ASIN", "orderedUnits": "Ordered Units"}, inplace = True)
        sales_report["Ordered Revenue"] = sales_report["orderedRevenue"].apply(lambda rev: rev["amount"])
        self.__remove_columns(sales_report)
        return sales_report

    @staticmethod
    def __remove_columns(sales_report:pd.DataFrame) -> None:
        logging.info("Removing the following columns: 'endDate', 'orderedRevenue', 'customerReturns', 'shippedCogs', 'shippedRevenue', 'shippedUnits'.")
        del sales_report["endDate"]
        del sales_report["orderedRevenue"]
        del sales_report["customerReturns"]
        del sales_report["shippedCogs"]
        del sales_report["shippedRevenue"]
        del sales_report["shippedUnits"]
