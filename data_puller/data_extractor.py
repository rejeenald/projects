from copy import deepcopy
import logging
from zprint_sku import ZprintSKU
from settings import SKU_COLOR_LOOKUP, PRODUCTION_DATA

class DataExtractor:
    def __init__(self) -> None:
        pass
        self.zprint_sku = ZprintSKU()
        self.orders = []
    
    def extract_data(self, orders:list) -> list:
        logging.info(f"Extracting significant columns...")
        for order in orders:
            self._set_store_id(order)
            self._set_recipient_details(order)
            self._set_order_items(order)

    def _set_order_items(self, order:dict) -> None:
        """If there quantity x is > 1 it should create x duplicate of the order."""
        items = order['items']
        item_count = self.__count_items(items)
        item_counter = 0
        for item in items:
            quantity = int(item['quantity'])
            for i in range(quantity):
                final_order = deepcopy(order)
                final_order = self._set_item_details(final_order, item)
                final_order['sku'] = item['sku']
                final_order['itemId'] = item['orderItemId']
                final_order["desc"] = self.__set_item_description(sku=item['sku'], color=final_order['color'], design=final_order['design'], desc=item['name']) # add color info here!)
                final_order['customizedURL'] = item['imageUrl']
                final_order['item_count'] = f"{order['orderNumber']}-{i+1}"
                final_order["address_verified"] = order["shipTo"]["addressVerified"]
                final_order["service_code"] = order["serviceCode"]
                
                item_counter += 1
                final_order["item_sku_count"] = f"{item_counter} of {item_count}"
                
                self.orders.append(final_order)
                logging.debug(f"Final orders: {final_order}")
    def __count_items(self, items) -> int:
        item_count = 0
        for item in items:
            quantity = int(item['quantity'])
            item_count += quantity
        return item_count

    def _set_item_details(self, order:dict, item:dict) -> None:
        # logging.info(f"order: {order}")
        color, design, model = None, None, None
        if self._has_item_options(item):
            if self._is_item_custom_order(item):
                options = item['options']
                logging.info(f"Custom /Z Item Found: {item['orderItemId']}.")
                logging.info(f"Unpacking options: {options}")
                color, design, model = self._unpack_cutom_order_item_options(options=options, sku=item["sku"])
            else:
                logging.warning(f"Not a custom order SKU for order itemid {item['orderItemId']}: {item['sku']}")
                order['sku'] = item['sku']
        else:
            logging.warning(f"No item options.")

        order['color'] = color
        order['design'] = design
        if model:
            order['sku'] = self.zprint_sku.fix_zprint_sku(item['sku'], model)

        return order
    
    @staticmethod
    def __set_item_description(sku:str, color:str, design:str, desc:str) -> str:
        if sku:
            if 'CUSTOM' in sku:
                if not color:
                    color = "---"
                if not design:
                    design = "---"
                return  f" [{color}]:[{design}] " + desc
        return desc

    @staticmethod
    def _has_item_options(item:dict) -> int:
        logging.info(f"Items: {item}")
        if len(item['options']) > 0 or not PRODUCTION_DATA:
            return True
        return False

    @staticmethod
    def _is_item_custom_order(item:dict) -> bool:
        logging.debug(f"Item reference for getting custom or z SKU: {item}")
        sku = item['sku']
        if sku:
            logging.info(f"Checking if SKU '{sku}' is custom order sku...")
            return "CUSTOM" in sku
        return False

    @staticmethod
    def _has_featured_sku(item:dict) -> bool:
        logging.debug(f"Item reference for getting featured SKU: {item}")
        sku = item['sku']
        if sku:
            logging.info(f"Checking if SKU '{sku}' if featured valid...")
            return "FEATURE" in sku
        return False


    @staticmethod
    def _set_store_id(order) -> None:
        logging.info("Extracting store id...")
        order['store'] = order['advancedOptions']['storeId']

    @staticmethod
    def _set_recipient_details(order) -> None:
        logging.info(f"Extracting customer details... ")
        shipTo = order['shipTo']
        order['name'] = shipTo['name']
        order['street1'] = shipTo['street1']
        order['street2'] = shipTo['street2']
        order['city'] = shipTo['city']
        order['state'] = shipTo['state']
        order['postalCode'] = shipTo['postalCode']
        order['country'] = shipTo['country']
        order['phone'] = shipTo['phone']

    def _unpack_cutom_order_item_options(self, options: list, sku:str):
        logging.info(f"Unpacking the array of options per of an item...")
        color, design, model = self.__set_defaults(sku=sku)
        for option in options:
            logging.info(f"options: {option}")
            if 'color' in option['name'].lower():
                color = option['value']
            elif 'design' in option['name'].lower():
                design = option['value']
            else:
                logging.warning(f"Unknown option name: {option['name']}")
        logging.info(f"color: {color}, design: {design}, model: {model}")
        
        return color, design, model

    @staticmethod
    def __set_defaults(sku:str):
        logging.debug(f"DEFAULT COLOR LOOKUPS FOR SKU: {SKU_COLOR_LOOKUP}")
        if sku in SKU_COLOR_LOOKUP.keys():
            logging.debug(f"SKU: {sku}")
            return SKU_COLOR_LOOKUP[sku], None, None
        return "Black Tie Affair", None, None