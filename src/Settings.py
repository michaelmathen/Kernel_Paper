
"""
This is a file of all the various data set files and global settings.
"""
import pyscan

CENSUS_BLOCKS = "/home/mmath/data/nhgis0003_shape/nhgis0003_shapefile_tl2010_us_tract_2010/US_tract_2010.shp"

EPS_BLOCKS = .010
# These are in meters
ALPHA_BLOCKS = 20000
R_MIN_BLOCKS = 20000
R_MAX_BLOCKS = 1000000
R_FRAC_BLOCKS = .1
P_BLOCK = .5
Q_BLOCK = .8
MAX_TIME_BLOCKS = 1000
COUNT_BLOCKS = 20
DISC_BLOCKS = pyscan.DISC