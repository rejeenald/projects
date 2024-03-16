import logging
import re
from settings import ZSKU_LOOKUP

class ZprintSKU:
    def __init__(self) -> None:
        pass

    def fix_zprint_sku(self, sku:str, model:str) -> str:
        logging.info(f"Fixing zprint sku because Zprint SKUs do not include the characters to denote the phone model, only the case family.")
        sku = self._extract_zprint_sku(sku)
        i = self._count_zprint_sku_prefix(sku)
        sku = self._generate_final_zprint_sku(sku, model, i)
        logging.info(f"Updated the sku to have the correct family/phone model: {sku}")
        return '-'.join(sku)

    @staticmethod
    def _extract_zprint_sku(sku:str) -> str:
        logging.info(f"Extracting one zprint sku for duplicated skus in a zprint item sku")
        if (sku[:1] == 'Z' or sku[:1] == 'z') and sku[0:5] == sku[6:11]:
            sku = sku[6:]
        sku.split('-')
        return sku

    @staticmethod
    def _count_zprint_sku_prefix(sku:str) -> int:
        logging.info(f"Counting the SLK and z/Z in the sku because they might duplicates of it in the sku.")
        i = 0
        while sku[i] == 'SLK' or re.match("[zZ]\\d{4}", sku[i]):
            i += 1
        return i

    @staticmethod
    def _generate_final_zprint_sku(sku:str, model:str, i:int) -> str:
        logging.info(f"Generating final zprint sku for {sku}")
        if len(sku[i]) <= 2:
            try:
                sku[i] += ZSKU_LOOKUP[model.lower()]
            except KeyError:
                logging.warning("Could not find iphone model and fix sku!")
        return sku

    

    

    