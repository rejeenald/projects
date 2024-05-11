import datetime as dt
import logging
import pandas as pd

from sc_reports import SCReports
from settings import MARKETPLACE_IDS, START_DATE, END_DATE

class SCCVR(SCReports):
    def __init__(self, country:str, filename:str="cvr_report") -> None:
        super().__init__(country=country)
        logging.info("\"===========================SCSales===========================\"")
        self.report_type = "GET_SALES_AND_TRAFFIC_REPORT"
        self.marketplace_id = MARKETPLACE_IDS[country]
        self.country = country
        self.report_data = None
        self.filename = filename

    def download_cvr_report(self) -> pd.DataFrame:
        logging.info(f"Downloading SC {self.country} Sales Report for date range {START_DATE}:{END_DATE}")
        current_date = START_DATE
        while current_date <= END_DATE:
            print("Current Date:", current_date)
            # Increment the current date by one day
            
            report_data = self.request_report( marketplace_id=self.marketplace_id, report_type=self.report_type, date_to_collect=current_date)
            report_data = self._format_downloaded_report(report_data=report_data)
            # table_name = "_".join(["cvr", self.country])
            # report_data.to_csv(f"{table_name}_{str(current_date)}.csv", index=False)
            self.save_report_to_db(report=report_data, table_name="sc_metrics", date_to_remove=current_date)
            current_date += dt.timedelta(days=1)
            logging.info(f"Next date: {current_date}")

    def _format_downloaded_report(self, report_data:pd.DataFrame) -> pd.DataFrame:
        logging.info(f"Fomatting downloaded sales report...")
        self.__rename_columns(report_data=report_data)
        self.__add_columns(report_data=report_data)
        self.__remove_columns(report_data=report_data)
        report_data = self.__make_date_column_first_column(report_data)
        logging.debug(f"CVR report:\n:{report_data}")
        return report_data
    
    def __rename_columns(self, report_data:pd.DataFrame) -> None:
        report_data.rename(columns={"parentAsin": "(Parent) ASIN", "childAsin": "(Child) ASIN"}, inplace=True)

    def __make_date_column_first_column(self, report_data) -> pd.DataFrame:
        return report_data[["Date"] + [col for col in report_data.columns if col != "Date"]]
    
    
    def __add_columns(self, report_data:pd.DataFrame) -> None:
        report_data["Sessions - Total"] = report_data.apply(lambda x: x["trafficByAsin"].get("sessions"), axis=1)
        report_data["Sessions - Total - B2B"] = report_data.apply(lambda x: x["trafficByAsin"].get("sessionsB2B"), axis=1)
        report_data["Session Percentage - Total"] = report_data.apply(lambda x: x["trafficByAsin"].get("sessionPercentage"), axis=1)
        report_data["Session Percentage - Total - B2B"] = report_data.apply(lambda x: x["trafficByAsin"].get("sessionPercentageB2B"), axis=1)
        report_data["Page Views - Total"] = report_data.apply(lambda x: x["trafficByAsin"].get("pageViews"), axis=1)
        report_data["Page Views - Total - B2B"] = report_data.apply(lambda x: x["trafficByAsin"].get("pageViewsB2B"), axis=1)
        report_data["Page Views Percentage - Total"] = report_data.apply(lambda x: x["trafficByAsin"].get("pageViewsPercentage"), axis=1)
        report_data["Page Views Percentage - Total - B2B"] = report_data.apply(lambda x: x["trafficByAsin"].get("pageViewsPercentageB2B"), axis=1)
        report_data["Featured Offer (Buy Box) Percentage"] = report_data.apply(lambda x: x["trafficByAsin"].get("buyBoxPercentage"), axis=1)
        report_data["Featured Offer (Buy Box) Percentage - B2B"] = report_data.apply(lambda x: x["trafficByAsin"].get("buyBoxPercentageB2B"), axis=1)

        report_data["Units Ordered"] = report_data.apply(lambda x: x["salesByAsin"].get("unitsOrdered"), axis=1)
        report_data["Units Ordered - B2B"] = report_data.apply(lambda x: x["salesByAsin"].get("unitsOrderedB2B"), axis=1)
        report_data["Ordered Product Sales"] = report_data.apply(lambda x: x["salesByAsin"].get("orderedProductSales").get("amount"), axis=1)
        report_data["Ordered Product Sales - B2B"] = report_data.apply(lambda x: x["salesByAsin"].get("orderedProductSalesB2B").get("amount"), axis=1)
        report_data["Total Order Items"] = report_data.apply(lambda x: x["salesByAsin"].get("totalOrderItems"), axis=1)
        report_data["Total Order Items - B2B"] = report_data.apply(lambda x: x["salesByAsin"].get("totalOrderItemsB2B"), axis=1)

        report_data["Unit Session Percentage"] = report_data.apply(lambda x: x["trafficByAsin"].get("unitSessionPercentage"), axis=1)
        report_data["Unit Session Percentage - B2B"] = report_data.apply(lambda x: x["trafficByAsin"].get("unitSessionPercentageB2B"), axis=1)


    def __remove_columns(self, report_data:pd.DataFrame) -> None:
        del report_data["salesByAsin"]
        del report_data["trafficByAsin"]