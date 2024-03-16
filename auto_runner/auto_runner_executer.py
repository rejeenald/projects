import logging
import pandas as pd
from auto_runner import AutoRunner
from settings import *
from custom_raw_data_updater import CustomRawDataUpdater
try:
    from op_sheets.op_sheet_batches import OpSheetGenerator
except:
    from .op_sheets.op_sheet_batches import OpSheetGenerator
from win32com import client


class AutoRunnerExecuter:
    def __init__(self, artboard:pd.DataFrame, regular:bool) -> None:
        logging.info("===============AutoRunnerExecuter===============")
        self.artboard = artboard
        self.auto_runner = AutoRunner()
        self.op_sheet_generator = OpSheetGenerator(artboard=artboard, regular=regular)
        self.custom_raw_data_updater = CustomRawDataUpdater()
        
    def execute_auto_runner(self) -> list:
        logging.info("Generating CSV and initial operatpr sheet...")
        self.op_sheet_generator.create_operator_sheets()
        self._create_artboards()
        self._update_custom_updater_file()

    def _create_artboards(self) -> None:
        logging.info("Creating artboard...")
        self.auto_runner.retrieve_generated_artboard_csvs_by_the_macro()
        self._create_artboard_for_6042_csvs()
        self._create_artboard_for_7151_csvs()
        logging.info("Done creating artboards!")

    def _update_custom_updater_file(self) -> None:
        logging.info("Updating the custom updater file...")
        self.custom_raw_data_updater.update_custom_updater_file_raw_data(item_ids_by_filename=self.op_sheet_generator.item_ids_by_filename)
        logging.info("Done making artboards!")

    def _create_artboard_for_7151_csvs(self) -> None:
        try:
            logging.info("Running for 7151 artboard...")
            self.auto_runner.create_artboards(printer='7151', artboard_csvs=self.auto_runner.artboard_csvs_7151)
        except Exception as e:
            logging.error(f"Failed to create artboard for 7151 CSVs: {e}")

    def _create_artboard_for_6042_csvs(self) -> None:
        try:
            logging.info("Running for 6042 arboard...")
            self.auto_runner.create_artboards(printer='6042', artboard_csvs=self.auto_runner.artboard_csvs_6042)
        except Exception as e:
            logging.error(f"Failed to create artboard for 6042 CSVs: {e}")