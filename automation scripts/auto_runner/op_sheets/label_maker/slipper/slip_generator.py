import img2pdf
import logging
import os

from .slipper_settings import SLIP_DIR
from .slip_maker import SlipMaker

class SlipGenerator:
    def __init__(self, order_dict:dict) -> None:
        logging.info("===============SlipGenerator===============")
        self.order_dict = order_dict
        self.orders_with_no_slip = []
        self.order_slip_already_created = []
        
    def generate_slips_to_slip_dir(self) -> None:
        logging.info(f"Generating the slips and saving it to {SLIP_DIR}.")
        self.__execute_slipper()
        self.__retrieve_pngs_from_slip_dir()
        logging.info("Done generating the slips!")

    def __execute_slipper(self) -> None:
        logging.info("Executing the SlipMaker methods!")
        slipper = SlipMaker(ss_data=self.order_dict)
        slipper.make_slips()
        self.orders_with_no_slip = slipper.no_slip_orders
        self.order_slip_already_created = slipper.order_slip_already_created

    @staticmethod
    def __retrieve_pngs_from_slip_dir() -> list:
        logging.info(f"SLIP_DIR: {SLIP_DIR}")
        slips = [f"{SLIP_DIR}\\{img}" for img in os.listdir(SLIP_DIR) if img.endswith('.pdf')]
        logging.info(f"Slips: {slips}")

    @property
    def no_slip_orders(self) -> list:
        return self.orders_with_no_slip

    @property
    def slip_already_created(self) -> list:
        return self.order_slip_already_created



    
    

    