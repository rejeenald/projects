import logging
import pandas as pd
from auto_runner_executer import AutoRunnerExecuter
from settings import ARTBOARD_ONLY

class ArtboardProcessor:
    def __init__(self, to_print_artboard:pd.DataFrame) -> None:
        self.to_print_artboard = to_print_artboard        
    
    def process_regular_artboard(self) -> None:
        logging.info("####### Processing Regular Artboards #######")
        artboard = self.to_print_artboard.loc[~self.to_print_artboard["Trim"].isin(["Gloss", "Dusk"]) & ~self.to_print_artboard["Color"].str.contains("CLEAR", case=False, na=False)]
        logging.info(f"Regular Artboard orders: {len(artboard)}")
        if not artboard.empty:
            try:
                artboard["family_sku"] = artboard.apply(lambda order: order["Sort Sku"].split(".")[0] if order["Sort Sku"].split(".")[0] != "SLK" else order["Sort Sku"].split(".")[1], axis=1)
                artboard.drop(["Printed?"], axis=1, inplace=True)
            except:
                artboard = pd.DataFrame()
        else:
            logging.info("No Regular Artboards Found!")
        print(f"Regular Artboard orders: {len(artboard)}")
        logging.info(f"Regular Artboard orders: {len(artboard)}")

        self._execute_auto_runner_with_this_artboard(artboard=artboard)

    def process_clear_artboard(self) -> None:
        logging.info("####### Processing Clear Artboards #######")
        clear_artboard = self.to_print_artboard[self.to_print_artboard["Color"].str.contains("CLEAR", case=False, na=False)]
        logging.info(f"Clear Artboard orders: {len(clear_artboard)}")
        if not clear_artboard.empty:
            try:
                clear_artboard["family_sku"] = clear_artboard.apply(lambda order: order["Sort Sku"].split(".")[0] if order["Sort Sku"].split(".")[0] != "SLK" else order["Sort Sku"].split(".")[1], axis=1)
                clear_artboard.drop(["Printed?"], axis=1, inplace=True)
            except:
                clear_artboard = pd.DataFrame()
        else:
            logging.info("No Clear Artboards Found!")
        print(f"Clear Artboard orders: {len(clear_artboard)}")
        logging.info(f"Clear Artboard orders: {len(clear_artboard)}")

        self._execute_auto_runner_with_this_artboard(artboard=clear_artboard, regular=False, clear_case=True)

    def process_amazon_artboard(self) -> None:
        """
        New Feature Request
        """
        logging.info("####### Processing Amazon Artboards #######")
        logging.info(f"Amazon Artboard orders: {len(self.to_print_artboard)}")
        if not self.to_print_artboard.empty:
            try:
                self.to_print_artboard["family_sku"] = self.to_print_artboard.apply(lambda order: order["Sort Sku"].split(".")[0] if order["Sort Sku"].split(".")[0] != "SLK" else order["Sort Sku"].split(".")[1], axis=1)
                self.to_print_artboard.drop(["Printed?"], axis=1, inplace=True)
            except:
                self.to_print_artboard = pd.DataFrame()
        else:
            logging.info("No Amazon Artboards Found!")
        print(f"Amazon Artboard orders: {len(self.to_print_artboard)}")
        logging.info(f"Amazon Artboard orders: {len(self.to_print_artboard)}")

        self._execute_auto_runner_with_this_artboard(artboard=self.to_print_artboard, regular=True)

    def _execute_auto_runner_with_this_artboard(self, artboard:pd.DataFrame, regular:bool=True, clear_case:bool=False):
        logging.debug(f"ARTBOARD ONLY: {ARTBOARD_ONLY}")
        if artboard.any or ARTBOARD_ONLY:
            logging.debug(f"execute auto_runner!")
            auto_runner = AutoRunnerExecuter(artboard=artboard, regular=regular, clear_case=clear_case)
            try:
                auto_runner.execute_auto_runner()   
            except Exception as e:
                logging.error(f"Failed to run auto runner: {e}")