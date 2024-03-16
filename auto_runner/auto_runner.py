import logging
import os
import pandas as pd

from artboard.artboard_creator_6042 import AIArtboardCreator_6042
from artboard.artboard_creator_7151 import AIArtboardCreator_7151
from settings import CSV_DIR, OP_SHEET_SUFFIX
from time import sleep


class AutoRunner:
    def __init__(self) -> None:
        logging.info("===============AutoRunner===============")
        self.artboard_creator_6042 = AIArtboardCreator_6042()
        self.artboard_creator_7151 = AIArtboardCreator_7151()

    def retrieve_generated_artboard_csvs_by_the_macro(self) -> None:
        files = self.__retrieve_csv_files()
        csv_files = self.__filter_out_non_csv_files(files=files)
        self.artboard_csvs_6042 = self.__retrieve_artboard_csvs(csv_files=csv_files, printer='6042')
        self.artboard_csvs_7151 = self.__retrieve_artboard_csvs(csv_files=csv_files, printer='7151')

    def create_artboards(self, printer:str, artboard_csvs:list) -> None:
        logging.info(f"Creating artboards for printer {printer}.")
        for filename in artboard_csvs:
            artboard_filename = CSV_DIR + filename
            try:
                self._create_artboards_for_csvs(printer=printer, filename=filename, artboard_filename=artboard_filename)
            except Exception as e:
                logging.error(f"Failed to create artwork for {filename}")

    def _create_artboards_for_csvs(self, printer:str, filename:str, artboard_filename:str) -> None:
        if printer == "6042":
            logging.info(f"Doin 6042 csv to generate 6042 eps files: {filename}")
            self.artboard_creator_6042.run_illustrator(artboard_filename)
            logging.info("Moving artboard csv to old jobs folder!")
            self.artboard_creator_6042.move_csv(filename)
        elif printer == "7151":
            logging.info(f"Doin 7151 csv to generate 7151 eps files: {filename}")
            self.artboard_creator_7151.run_illustrator(artboard_filename)
            logging.info("Moving artboard csv to old jobs folder!")
            self.artboard_creator_7151.move_csv(filename)
            

    @staticmethod
    def __retrieve_csv_files() -> list:
        f = os.listdir(CSV_DIR)
        if f:
            logging.info(f"Found {len(f)} folders/files.")
            return f
        logging.warning(f"No folders/files found: {len(f)}")
        return []

    @staticmethod
    def __filter_out_non_csv_files(files:list) -> list:
        csv_files = []
        skipped_files = []
        for f in files:
            if f.endswith('.csv'):
                csv_files.append(f)
            else:
                skipped_files.append(f)

        logging.info(f"Skipped files: {skipped_files}")
        logging.info(f"CSV Files: {csv_files}")
        return csv_files

    @staticmethod
    def __retrieve_artboard_csvs(csv_files:list, printer:str) -> list:
        artboard_csvs = []
        printer_code = f"--{printer}--"
        for csv in csv_files:
            if csv.endswith(f"{OP_SHEET_SUFFIX}.csv") and printer_code in csv:
                artboard_csvs.append(csv)
        
        logging.info(f"Artboard CSV Files: {artboard_csvs}")
        return artboard_csvs