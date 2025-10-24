import logging

class PackingSlipData:
    def __init__(self, order:dict):
        logging.info(f"=================PackingSlipData=================")
        self.data = {
            "shipping_address": self._compose_address(order=order),
            "order_number": order.get("orderNumber"),
            "date": order.get("date"),
            "items": order.get("items")
        }

    @staticmethod
    def _compose_address(order:dict) -> str:
        logging.info("Composing the address")
        address_1 = order["address1"]
        address_2 = order["address2"]
        if address_1:
            name_address_1 = "\n".join([order["name"], address_1])
        else:
            name_address_1 = order["name"]

        if isinstance(address_2, str):
            address_2_location = "\n".join([address_2, order["location"]])
        else:
            address_2_location = order["location"]

        return " ".join([name_address_1, address_2_location])

    @property
    def slip_data(self):
        flat = self.data.copy()
        items = flat.pop("items", [])
        for idx, item in enumerate(items, start=1):
            flat[f"sku_{idx}"] = item["sku"]
            flat[f"description_{idx}"] = item["desc"]
            flat[f"qty_{idx}"] = item["qty"]
        return flat