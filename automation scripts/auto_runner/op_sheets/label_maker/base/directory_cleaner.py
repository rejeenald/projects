import logging
import os

from .base_settings import CONFIRMATION_FILES_DIR, LABEL_DIR, SLIP_DIR

class DirectoryCleaner:
    def __init__(self) -> None:
        logging.info("===============DirectoryCleaner===============")

    def clean_confirmation_files_dir(self, conf_files:bool=False) -> None:
        logging.info("Cleaning the CONFIRMATION_FILES_DIR!")
        if conf_files:
            try:
                self._remove_conf_files()
            except FileNotFoundError:
                logging.critical("Confirmation not found! Please pull labels manually")

    def clean_label_dir(self) -> None:
        logging.info("Cleaning the LABEL_DIR!")
        for label in os.listdir(LABEL_DIR):
            os.remove(LABEL_DIR + fr"\\{label}")

    def clean_slip_dir(self) -> None:
        logging.info("Cleaning the SLIP_DIR!")
        for slip in os.listdir(SLIP_DIR):
            os.remove(SLIP_DIR + fr"\\{slip}")

    @staticmethod
    def _remove_conf_files() -> None:
        for conf_file in os.listdir(CONFIRMATION_FILES_DIR):
            conf_file_path = CONFIRMATION_FILES_DIR + fr"\\{conf_file}"
            print(conf_file_path)
            os.remove(conf_file_path)

    