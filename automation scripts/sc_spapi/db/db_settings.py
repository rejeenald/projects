import sys
sys.path.append("..")
from settings import SYNCPLICITY_ROOT
from .mock_df import MOCK_DF

DB_PRODUCTION = True
TEST_TABLE = False
TEST_TABLE_COLS = ["title", "year"]

if DB_PRODUCTION:
    DB_PATH = SYNCPLICITY_ROOT + "-------------------.db"
else:
    DB_PATH = SYNCPLICITY_ROOT + "-------------------.db"
    MOCK_DF = MOCK_DF
