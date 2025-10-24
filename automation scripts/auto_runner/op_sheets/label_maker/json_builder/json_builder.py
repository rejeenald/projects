import logging
import pandas as pd
from random import randrange

from .orders_verifier import OrderVerifier
from .json_builder_settings import UNSHIPPED_ORDERS

class JSONBuilder:
    def __init__(self, pdf_name:str) -> None:     
        logging.info("===============JSONBuilder===============")
        self.order_dict = {
                "orders": [],
                "confirmationFile": f"{randrange(16 ** 32):030x}"
            }
        self.pdf_name = pdf_name
        self.unshipped_orders = None
        self.unverified_orders = []

    def build_json(self, orders_id:list=[]) -> (dict, list, list):
        logging.info("Building JSON!")
        
        self._set_unshipped_orders(orders_id=orders_id)
        logging.info("Done building JSON!")

    def _set_unshipped_orders(self, orders_id:dict={}) -> None:
        logging.info("Setting unshipped orders: unverified and unshipped!")
        unshipped = self.__retrieve_unshipped_orders(orders_id=orders_id)
        self.order_verifier = OrderVerifier(unshipped=unshipped, pdf_name=self.pdf_name)
        self.order_verifier.verify_orders()
        self.unshipped_orders = self.order_verifier.unshipped_formatted
        self.unverified_orders = self.order_verifier.unshipped_unverified
        
    def __retrieve_unshipped_orders(self, orders_id:dict={}) -> pd.DataFrame:
        logging.info(f"Retrieving the unshipped orders from orders.csv: {UNSHIPPED_ORDERS}")
        try:
            logging.debug("Reading with encoding utf-8")
            unshipped = pd.read_csv(UNSHIPPED_ORDERS, low_memory=False, encoding="utf-8")
        except Exception as e:
            logging.debug(f"Reading with encoding ISO-8859-1: {e}")
            unshipped = pd.read_csv(UNSHIPPED_ORDERS, low_memory=False, encoding="ISO-8859-1")

        unshipped = self._pick_unshipped_orders(unshipped_orders=unshipped, order_ids=orders_id)
        logging.debug(f"Unshipped: {unshipped}")
        return unshipped

    @staticmethod
    def _pick_unshipped_orders(unshipped_orders:pd.DataFrame, order_ids:list) -> pd.DataFrame:
        logging.info(f"Picking unshipped orders by its orders ids provided: {order_ids}")
        unshipped = []
        unshipped_orders = unshipped_orders.to_dict("records")
        # logging.debug(f"Unshipped orders: {unshipped_orders}")
        for o_id in order_ids:
            logging.debug(f"order id: {o_id} -> type: {type(o_id)}")
            logging.debug(f"type: {type(unshipped_orders)}")
            for order_index in range(0, len(unshipped_orders)):
                # logging.debug(f"order_index: {order_index}")
                ordr = unshipped_orders[order_index]
                # logging.debug(f"order to compare: {(ordr['orderId'])}")
                if ordr['orderId'] == o_id:
                    logging.debug(f"Found order id matched: {ordr}")
                    unshipped.append(ordr)
                    del unshipped_orders[order_index]
                    break
        logging.debug(f"Unshipped: {unshipped}")
        unshipped_df = pd.DataFrame(unshipped)
        return unshipped_df

    @property
    def order_dict_with_unships(self) -> dict:
        self.order_dict["orders"] = self.unshipped_orders
        return self.order_dict

    @property
    def unverified(self) -> list:
        return self.unverified_orders
    
# if __name__ == "__main__":
#     j = JSONBuilder(pdf_name="sample.pdf")
#     j.build_json(orders_id=['1068253462'])
#     unshipped = j.order_dict_with_unships
    # print(unshipped)
    # unshipped_df = pd.DataFrame.from_dict(unshipped, orient="columns")
    # print(type(unshipped_df))
    # unshipped.to_csv("unshipped_test.csv")
