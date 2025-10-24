import logging, os, traceback

from random import randint
from time import sleep

from .slipper_settings import CONFIRMATION_FILES_DIR, BACKUP_LABEL_DIR
from .label_puller import LabelPuller
from .slip_pdf_editor import SlipPDFEditor


class SlipMaker:
    def __init__(self, ss_data:dict={}, find_backup_labels:bool=True) -> None:
        logging.info("===============SlipMaker===============")
        self.orders = ss_data["orders"]
        self.find_backup_labels = find_backup_labels
        self.confirmation_file = ss_data["confirmationFile"]
        self.order_ids = []
        self.orders_with_no_slips = []
        self.order_slip_already_created = []

    def make_slips(self) -> None:
        logging.info("Making slips method now...")
        counter = 10
        for order in self.orders:
            try:
                label_info = self._pull_label_from_shipstation(order=order, find_backup_labels=self.find_backup_labels, counter=counter)
            except Exception as e:
                logging.error(f"ShipStation Issue: {e}")
                label_info["status"] = "fail"
                label_info["data"] = "ShipStation Issue"
                logging.warning(f"Adding to orders with no slips: {order['orderNumber']}")
                self.orders_with_no_slips.append([order['orderNumber'], order['name']])
                
            if label_info and label_info["status"] != "fail":
                self._create_slip(order=order, label_path=label_info["data"], slip_filename=str(counter))
            counter += 1            
        self._save_confirmation_data_to_textfile()
        logging.info("Done making the slips!")

    def _save_confirmation_data_to_textfile(self):
        confimation_filepath = CONFIRMATION_FILES_DIR + f"\\{self.confirmation_file}" + ".txt"
        self.writeFile(confimation_filepath)

    def _pull_label_from_shipstation(self, order:dict, find_backup_labels:bool, counter:int) -> dict:
        label_puller = LabelPuller(order=order, find_backup_labels=find_backup_labels, slip_counter=counter)
        label_info = label_puller.pull_label()
        if label_info["status"] == "pulled previously":
            self.order_slip_already_created.append([order['orderNumber'], order['name']])
            return
        if label_info["status"] == "fail":
            if self.__is_saved_in_backup_label_dir(order['orderId']):
                label_info["status"] = "pass"
                label_info["data"] = f"{BACKUP_LABEL_DIR}\\{order['orderId']}.pdf"
            else:
                logging.warning(f"Adding to orders with no slips: {order['orderNumber']}")
                self.orders_with_no_slips.append([order['orderNumber'], order['name']])
        return label_info

    @staticmethod
    def _create_slip(order:dict, label_path:dict, slip_filename:str) -> None:
        slip_pdf_builder = SlipPDFEditor(order=order, label_path=label_path, slip_filename=slip_filename)
        try:
            logging.info("Trying to create a slip using PDF Slip Builder")
            slip_pdf_builder.create_slip()
        except Exception as e:
            logging.error(f"Failed to create a packing slip using PDF Slip Builder: {e}")
            logging.debug(traceback.format_exc())
            logging.info(f"Retrying...")
            sleep(0.5)
            slip_pdf_builder.create_slip()

    @staticmethod
    def __is_saved_in_backup_label_dir(order_id:int) -> bool:
        logging.info("Finding the label in the BACKUP_LABEL_DIR...")
        for label in os.listdir(BACKUP_LABEL_DIR):
            if label == f"{order_id}.pdf":
                logging.info(f"Found label {label} in BACKUP_LABEL_DIR of order {order_id}")
                return True
        return False

    @staticmethod
    def writeFile(filename) -> None:
        open(filename, "w").close()

    @property
    def no_slip_orders(self) -> list:
        return self.orders_with_no_slips

    @property
    def slip_already_created(self) -> list:
        return self.order_slip_already_created