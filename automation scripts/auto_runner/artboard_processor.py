import logging
import pandas as pd
from auto_runner_executer import AutoRunnerExecuter

class ArtboardProcessor:
    def __init__(self, to_print_artboard:pd.DataFrame) -> None:
        self.to_print_artboard = to_print_artboard        
    
    def process_regular_artboard(self) -> None:
        logging.info("####### Processing Regular Artboard #######")
        artboard = self.to_print_artboard.loc[~self.to_print_artboard["Trim"].isin(["Gloss"]) & ~self.to_print_artboard["Trim"].isin(["Dusk"])]
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

    def process_gloss_artboard(self) -> None:
        logging.info("####### Processing Gloss Artboard #######")
        gloss_arboard = self.to_print_artboard.loc[self.to_print_artboard["Trim"].isin(["Gloss"])]
        logging.info(f"Gloss Artboard orders: {len(gloss_arboard)}")
        if not gloss_arboard.empty:
            try:
                gloss_arboard["family_sku"] = gloss_arboard.apply(lambda order: order["Sort Sku"].split(".")[0] if order["Sort Sku"].split(".")[0] != "SLK" else order["Sort Sku"].split(".")[1], axis=1)
                gloss_arboard.drop(["Printed?"], axis=1, inplace=True)
            except:
                gloss_arboard = pd.DataFrame()
        else:
            logging.info("No Gloss Artboards Found!")
        print(f"Gloss Artboard orders: {len(gloss_arboard)}")
        logging.info(f"Gloss Artboard orders: {len(gloss_arboard)}")

        self._execute_auto_runner_with_this_artboard(artboard=gloss_arboard, regular=False)

    def process_dusk_artboard(self) -> None:
        logging.info("####### Processing Dusk Artboard #######")
        dusk_artboard = self.to_print_artboard.loc[self.to_print_artboard["Trim"].isin(["Dusk"])]
        logging.info(f"Dusk Artboard orders: {len(dusk_artboard)}")
        if not dusk_artboard.empty:
            try:
                dusk_artboard["family_sku"] = dusk_artboard.apply(lambda order: order["Sort Sku"].split(".")[0] if order["Sort Sku"].split(".")[0] != "SLK" else order["Sort Sku"].split(".")[1], axis=1)
                dusk_artboard.drop(["Printed?"], axis=1, inplace=True)
            except:
                dusk_artboard = pd.DataFrame()
        else:
            logging.info("No Dusk Artboards Found!")
        print(f"Dusk Artboard orders: {len(dusk_artboard)}")
        logging.info(f"Dusk Artboard orders: {len(dusk_artboard)}")

        self._execute_auto_runner_with_this_artboard(artboard=dusk_artboard, regular=False)

    def _execute_auto_runner_with_this_artboard(self, artboard:pd.DataFrame, regular:bool=True):
        if artboard.any:
            auto_runner = AutoRunnerExecuter(artboard=artboard, regular=regular)
            try:
                auto_runner.execute_auto_runner()   
            except Exception as e:
                logging.error(f"Failed to run auto runner: {e}")