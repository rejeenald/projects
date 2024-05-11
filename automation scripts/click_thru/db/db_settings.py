import sys
sys.path.append("..")
from settings import SYNCPLICITY_ROOT

DB_PRODUCTION = True

if DB_PRODUCTION:
    DB_PATH = SYNCPLICITY_ROOT + "-------"
else:
    DB_PATH = SYNCPLICITY_ROOT + "-------"