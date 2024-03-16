import sys
sys.path.append("..")
from settings import SYNCPLICITY_ROOT, CSV_DIR, OLD_JOB_DIR, PRODUCTION_EPS, RESULTS_PATH


#MAKE SURE POSITION ANCHOR POINT IS SET TO CENTER WHEN COPYING POINT POSITIONS
# HARDCODE IN JIG POSITIONS 
# Hard code in x,y positions of jig positions

#Point 1
p0X = 1412.5
p0Y = 1062.25

#Point 2
p1X = 872.5
p1Y = 1062.25

#Point 3
p2X = 332.5 
p2Y = 1062.25

#Point 4
p3X = 1412.5
p3Y = 756.25

#Point 5
p4X = 872.5
p4Y = 756.25

#Point 6
p5X = 332.5
p5Y = 756.25

#Point 7
p6X = 1412.5
p6Y = 450.25

#Point 8
p7X = 872.5
p7Y = 450.25

#Point 9
p8X = 332.5
p8Y = 450.25

#Point 10
p9X = 1412.5
p9Y = 144.25

#Point 11
p10X = 872.5
p10Y = 144.25

#Point 12
p11X = 332.5
p11Y = 144.25


JIGPOSITIONS_X_6042 = [p0X, p1X, p2X, p3X, p4X, p5X, p6X, p7X, p8X, p9X, p10X, p11X]
JIGPOSITIONS_Y_6042 = [p0Y, p1Y, p2Y, p3Y, p4Y, p5Y, p6Y, p7Y, p8Y, p9Y, p10Y, p11Y]
UP_JIG_6042 = SYNCPLICITY_ROOT + r"\Production\_Custom Jig\6042-current-jig-ab.ai"
CSV_DIR = CSV_DIR
OLD_JOB_DIR = OLD_JOB_DIR

if PRODUCTION_EPS:
    DESTINATION_FOLDER_6042 = SYNCPLICITY_ROOT + r"\Production\6042 Jobs"
else:
    DESTINATION_FOLDER_6042 = RESULTS_PATH + r"\Production\6042 Jobs"


print(f"JIGPOSITIONS_X_6042: {JIGPOSITIONS_X_6042}")
print(f"JIGPOSITIONS_Y_6042: {JIGPOSITIONS_Y_6042}")