import datetime as dt
import logging
import pandas as pd

from vc_reports import VCReports
from settings import MARKETPLACE_IDS, FORECASTING_COLUMNS, FORECASTING_WEEKS

class VCForecasting(VCReports):
    def __init__(self, country:str="US", filename:str="forecasting") -> None:
        super().__init__()
        self.report_type = "GET_VENDOR_FORECASTING_REPORT"
        self.marketplace_id = MARKETPLACE_IDS[country]
        self.country = country
        self.report_data = None
        self.filename = filename

    def download_report(self) -> pd.DataFrame:
        logging.info(f"Downloading VC {self.country} Forecasting Report...")
        report_data = self.request_report(marketplace_id=self.marketplace_id, report_type=self.report_type, forecasting=True)
        # logging.debug(f"VC forecasting: {report_data}")
        forecasting_report = pd.DataFrame.from_records(report_data["forecastByAsin"])
        forecasting_report = self._format_downloaded_report(forecasting_report=forecasting_report)
        self.save_report_to_db(report=forecasting_report, table_name="vc_forecast")

    def _format_downloaded_report(self, forecasting_report:pd.DataFrame) -> pd.DataFrame:
        logging.info(f"Fomatting downloaded forecasting report...")
        forecasting_report.rename(columns = {"asin": "ASIN", "startDate": "WEEK", "meanForecastUnits": "MEAN"}, inplace = True)
        forecasting_report = self.__remove_columns(forecasting_report=forecasting_report)
        forecasting_report = forecasting_report.pivot_table(values="MEAN", index="ASIN", columns="WEEK").reset_index()
        forecasting_report = forecasting_report.iloc[:, 0:FORECASTING_WEEKS+1]
        forecasting_report = self.__rename_week_columns(forecasting_report=forecasting_report)
        return forecasting_report

    @staticmethod
    def __rename_week_columns(forecasting_report:pd.DataFrame) -> pd.DataFrame:
        logging.info("Renaming weeks columns to 'Week  (0-8) - Mean Forecast'...")
        cols = forecasting_report.columns
        counter = 0
        for col_index in range(1,FORECASTING_WEEKS+1):
            forecasting_report.columns.values[col_index] = f"Week  {counter} - Mean Forecast"
            counter += 1
        return forecasting_report

    @staticmethod
    def __remove_columns(forecasting_report:pd.DataFrame) -> None:
        logging.info(f"Retaining initial forecasting columns: {FORECASTING_COLUMNS}")
        return forecasting_report[FORECASTING_COLUMNS]