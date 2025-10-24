import logging

from .slipper_settings import PACKING_SLIP_TEMPLATE, PACKING_SLIP_MULTI_TEMPLATE, PACKING_SLIP_DIRECT_FULFILLMENT_TEMPLATE

class SlipTemplate:
    def __init__(self) -> None:
        logging.info("===============SlipTemplate===============")
        self.custom_slip_stores = {}
        self.custom_slip_stores["413731"] = PACKING_SLIP_DIRECT_FULFILLMENT_TEMPLATE
        self.packing_slip_template = PACKING_SLIP_TEMPLATE
        self.packing_slip_template_multi = PACKING_SLIP_MULTI_TEMPLATE

    def select_template(self, order:dict) -> str:
        logging.info("Selecting Templaing method...")
        template_filename = self._retrieve_appropriate_template_file(order)
        logging.debug(f"Template filename: {template_filename}")
        return template_filename

    def _retrieve_appropriate_template_file(self, order:dict) -> str:
        logging.info("storeId: {}".format(order["storeId"]))
        if self.__is_store_has_custom_slip(order):
            logging.info(f"Custom store: {order['storeId']} ")
            return self.custom_slip_stores[str(order["storeId"])]
        elif self.__is_order_has_multiple_items(order):
            logging.info("Order items > 1: multi items")
            return self.packing_slip_template_multi
        elif self.__is_order_has_more_one_qty(order):
            logging.info(f"Order item qty > 1: multiple quantity")
            return self.packing_slip_template_multi
        else:
            logging.info("Using the regular template instead!")
            return self.packing_slip_template

    def __is_store_has_custom_slip(self, order:dict) -> bool:
        return str(order["storeId"]) in self.custom_slip_stores

    @staticmethod
    def __is_order_has_multiple_items(order:dict) -> bool:
        return len(order["items"]) > 1

    @staticmethod
    def __is_order_has_more_one_qty(order:dict) -> bool:
        return order["items"][0]["qty"] > 1
