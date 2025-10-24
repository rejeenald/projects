import logging
import pandas as pd

from random import randint
from time import sleep

from .json_builder_settings import JSON_HEADERS, UNVERIFIED_ORDERS, VERIFIED_ORDERS, SHIPSTATION_ACCESS

class OrderVerifier:
    def __init__(self, unshipped:pd.DataFrame, pdf_name:str) -> None:
        logging.info("===============OrderVerifier===============")
        self.country = "US"
        self.orders = unshipped
        self.ssapi = SHIPSTATION_ACCESS
        self.pdf_name = pdf_name
            
    def verify_orders(self) -> (list, list):
        logging.info(f"Verifying unshipped orders!")
        logging.debug(f"Type of orders: {type(self.orders)}")
        if not self.orders.empty:
            self._count_unique_orders()
            self._set_data_for_slipper()
            self._retain_required_columns()
            self._merge_orders_with_the_same_order_ids()
            logging.info("Done verifying the orders!")
        else:
            logging.info("No Order Ids to count and verify!")

    def _count_unique_orders(self) -> None:
        self.orders["qty"] = self.orders.groupby(["orderId", "itemId"])["orderId"].transform("count")
        self.orders.drop_duplicates(keep="last", inplace=True)

    def _set_data_for_slipper(self) -> None:
        logging.info(f"Setting data for the sliper: {len(self.orders)}")
        self.orders["location"] = self.orders.apply(lambda x: self.__set_location(order_data=x), axis=1)
        self.orders["date"] = self.orders.apply(lambda x: self.__set_date(order_data=x), axis=1)
        self.orders["items"] = self.orders.apply(lambda x: self.__set_items(order_data=x), axis=1)
        self.orders["validated"] = self.orders.apply(lambda x: self.__verify_order_address(order_data=x), axis=1)
        self.orders["status"] = self.orders.apply(lambda x: x["orderStatus"], axis=1)
        self.orders["address1"] = self.orders.apply(lambda x: x["street1"], axis=1)
        self.orders["address2"] = self.orders.apply(lambda x: x["street2"], axis=1)
        self.orders["storeId"] = self.orders.apply(lambda x: x["store"], axis=1)
        logging.info(f"Done setting data for slipper!")
        
    def _retain_required_columns(self) -> None:
        self.orders = self.orders[JSON_HEADERS]
    
    def _merge_orders_with_the_same_order_ids(self) -> None:
        logging.info("Merging orders with tge same order ids")
        orders = self.orders.to_dict("records")
        merged_orders = {}
        for order in orders:
            o_id = order["orderId"]
            if o_id in merged_orders.keys():
                merged_orders[o_id]["items"] = self.__set_items_removing_duplicates(merged_items=merged_orders[o_id]["items"], order_items=order["items"])
            else:
                merged_orders[o_id] = order
    
        self.orders = pd.DataFrame(merged_orders.values())
        logging.debug(f"orders>>>: {self.orders}")

    @staticmethod
    def __set_items_removing_duplicates(merged_items:dict, order_items:dict) -> dict:
        merged_items = merged_items + order_items
        items = [dict(t) for t in {tuple(itm.items()) for itm in merged_items}]
        logging.debug(f"Items after removing duplicates: {items}")
        return items
    
    def __set_location(self, order_data:dict) -> str:
        # logging.debug("Setting location...")
        location = f"{order_data['city']}, {order_data['state']} {order_data['postalCode']}"
        if self.__is_within_US(order=order_data):
            return location
        else:
            return f"{location} {order_data['country']}"

    def __set_date(self, order_data:dict) -> str:
        logging.debug("Setting location...")
        date = order_data['orderDate'][:10].split('-')
        if self.__is_within_US(order=order_data):
            return f"{date[1]}/{date[2]}/{date[0]}"
        else:
            return f"{date[2]}/{date[1]}/{date[0]}"

    def __is_within_US(self, order:dict) -> bool:
        return order['country'] == self.country

    def __set_items(self, order_data:dict) -> dict:
        if order_data["item_sku_count"] != "1 of 1":
            logging.info(f"Multi sku item. Requesting the order data of order {order_data['orderNumber']} to update items!")
            sleep_time = randint(1,5)
            logging.info(f"Taking a pause before sending request to ShipStation: {sleep_time}")
            sleep(sleep_time)
            
            order = self.ssapi.get_order(order_id=order_data.get("orderId"))
            return self.__set_items_for_multi__(order=order)
        return [{
            "sku": order_data['sku'],
            "desc": order_data['desc'],
            "qty": order_data['qty']
            }]

    def __set_items_for_multi__(self, order:dict) -> list:
        items = order.get("items")
        items_fnl = []
        for item in items:
            items_fnl.append({"sku": item['sku'],"desc": item['name'],"qty": item['quantity'], 'item_id':item['orderItemId']})
        logging.debug(f"order id: {order.get('orderId')} >>> final items: {items_fnl}")
        return items_fnl
    
    @staticmethod
    def __verify_order_address(order_data:dict) -> bool:
        logging.debug("Verifying order address...")
        logging.debug(f"order {order_data['orderNumber']} with items {order_data['items']}")
        if order_data["address_verified"] == 'Address validated successfully':
            return True
        else:
            return False  

    @property
    def unshipped_formatted(self) -> list:
        # print(f"unshipped: {self.orders}")
        unshipped_formatted= self.orders[self.orders["validated"] == True]
        op_sheet_name = self.pdf_name.split('\\')[-1]
        filepath = VERIFIED_ORDERS + f"{op_sheet_name}.csv"
        logging.info(f"Filepath of unshipped formatted: {filepath}")
        unshipped_formatted.to_csv(filepath, index=False)
        if len(unshipped_formatted.index) > 0:
            orders_list = unshipped_formatted.to_dict("records")
        else:
            orders_list = []
        return orders_list

    @property
    def unshipped_unverified(self) -> list:
        unverified= self.orders[self.orders["validated"] == False]
        op_sheet_name = self.pdf_name.split('\\')[-1]
        filepath = UNVERIFIED_ORDERS + f"{op_sheet_name}.csv"
        logging.info(f"Filepath of unshipped unverified: {filepath}")
        unverified.to_csv(filepath, index=False)
        if len(unverified.index) > 0:
            orders_list = unverified.to_dict("records")
        else:
            orders_list = []
        return orders_list