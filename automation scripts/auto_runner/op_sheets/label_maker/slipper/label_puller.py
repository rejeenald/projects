
import logging, os
from base64 import b64decode
from time import sleep
from unittest import runner

from .slipper_settings import BACKUP_LABEL_DIR, LABEL_DIR, TESTING, SHIPSTATION_ACCESS

class SSFailedToProvideLabel(Exception):
    pass

class RateLimitException(Exception):
    pass

class LabelPuller:
    def __init__(self, order:dict, find_backup_labels:bool, slip_counter:int) -> None:
        logging.info("===============LabelPuller===============")
        self.order = order
        self.find_backup_labels = find_backup_labels
        self.slip_counter = slip_counter
        self.label_info = {"status": "unknown", "data": ""}
        self.ssapi = SHIPSTATION_ACCESS
    
    def pull_label(self) -> dict:
        logging.info("Pulling label...")
        order_id = self.order["orderId"]
        if self.find_backup_labels:
            logging.info("Checking if label is already pulled and already in BACKUP_LABEL_DIR directory.")
            label_info = self._find_backup_label_from_backup_label_dir(order_id=order_id)
            if label_info:
                return label_info
        
        logging.info("No backup label found! Pulling label from ShipStation...")
        return self._pull_label_from_shipstation()
        
    def _find_backup_label_from_backup_label_dir(self, order_id:int) -> dict:
        logging.info(f"Checking the BACKUP_LABEL_DIR to verify if the order {order_id} label has previously already.")
        label_info = {}
        backup = self.__find_backup_label(order_id=order_id)
        if backup:
            label_info["status"] = "pulled previously"
            label_info["data"] = "Previosuly pulled label, previously! Not pulling anymore!"
        logging.debug(f"label_info: {label_info}")
        return label_info

    def _pull_label_from_shipstation(self) -> dict:
        logging.info(f"Pulling label from the ShipStation for this order: {self.order['name']}")
        if self.__is_order_valid(order=self.order):
            logging.info(f"Order of {self.order['name']} is valid!")
            return self.__extract_valid_order_label_info()
        else:
            logging.info(f"Order of {self.order['name']} is invalid!")
            return self.__extract_invalid_order_label_info()

    def __extract_valid_order_label_info(self) -> dict:
        order_id = self.order["orderId"]
        service_code = self.order["service_code"]
        logging.info(f"Getting Label for {self.order['orderNumber']}")
        label_info = self.___pull_label(order_id=order_id, test_label=TESTING, service_code=service_code)

        logging.info("Transforming labelData to a pdf version of the order label!")
        return self.___convert_label_to_pdf(label_info=label_info, order=self.order)

    def __extract_invalid_order_label_info(self) -> dict:
        logging.info(f"Setting label_info for the failed order: {self.order['orderNumber']}")
        label_info = {"status": "fail"}
        if self.__is_order_cancelled(order=self.order):
            label_info["data"] = "cancelled"
        else:
            label_info["data"] = "unknown"
        logging.debug(f"label_info: {label_info}")
        return label_info

    def ___pull_label(self, order_id:int, test_label:bool, service_code:str) -> dict:
        label_info = {"labelData": None}
        try:
            logging.info(f"Trying to create label for order: {order_id}")
            label_info = self.ssapi.create_label_for_order(order_id=order_id, service_code=service_code, test_label=test_label)
        except KeyError as e:
            logging.warning(f"KeyError 237: Failure occurred while pulling label for order {order_id} Error response dump:{e}")
            logging.debug(f"label info returned: {label_info}")
            label_info["status"] = "fail"
            label_info["data"] = f"Failure occurred while pulling label for order {order_id} Error response  dump:{e}"
        except Exception as e:
            logging.warning(f"Error 244: Failure occurred while pulling label for order {order_id} Error response  dump:{e}")
            logging.debug(f"label info returned: {label_info}")
            label_info["status"] = "fail"
            label_info["data"] = f"Failure occurred while pulling label for order {order_id} Error response  dump:{e}"

        return label_info      

    def ___convert_label_to_pdf(self, label_info:dict, order:dict) -> dict:
        try:
            label = b64decode(label_info.get('labelData'), validate=True)
        except SSFailedToProvideLabel as e:
            logging.warning(f"ShipStation did not provide label data.'labelData' does not exist. Failed to convert to pdf using the b64decode: {e}")
            label_info["status"] = "fail"
            label_info["data"] = "'labelData' does not exist. Failed to convert to pdf using the b64decode"
            return label_info
        except Exception as e:
            logging.warning(f"Shipstation API issue: {e}")
            label_info["status"] = "fail"
            label_info["data"] = "Failed to pull label for unknown reasons!"
            return label_info

        return self.____save_label_to_directory___(label=label, order=order)
    
    @staticmethod
    def __find_backup_label(order_id:int) -> str:
        logging.info("Finding the label in the BACKUP_LABEL_DIR")
        for label in os.listdir(BACKUP_LABEL_DIR):
            if label == f"{order_id}.pdf":
                logging.info(f"Found label {label} in BACKUP_LABEL_DIR of order {order_id}")
                return f"{BACKUP_LABEL_DIR}\\{order_id}.pdf"
        return ''

    @staticmethod
    def __is_order_valid(order:dict) -> bool:
        if order:
            if order['validated'] and order["status"] != "shipped":
                if order["status"] != "cancelled" and order["status"] != "unknown error":
                    return True
        return False

    @staticmethod
    def __is_order_cancelled(order:dict) -> bool:
        if order["status"] == "cancelled":
            return True
        return False


    def ____save_label_to_directory___(self, label, order:dict) -> dict:
        logging.debug(f"label into b64decode: {len(label)}")
        
        logging.info(f"Saving to {LABEL_DIR}")
        label_dir_slip_filename = f"{LABEL_DIR}\{order['orderId']}.pdf"
        with open(label_dir_slip_filename, "wb") as f:
            f.write(label)

        logging.info(f"Saving to {BACKUP_LABEL_DIR}")
        backup_label_dir_slip_filename = f"{BACKUP_LABEL_DIR}\{order['orderId']}.pdf"
        with open(backup_label_dir_slip_filename, "wb") as f:
            f.write(label)
        
        label_info = {}
        label_info["status"] = "pass"
        label_info["data"] = label_dir_slip_filename
        logging.debug(f"Label info: {label_info}")

        return label_info