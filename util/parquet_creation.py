import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")
data_path = Path("../data")
# data_path = Path('data')
config = pd.read_excel(data_path / "config.xlsx", sheet_name="layers")
config.tail(3)

def get_layer(row):
    try:
        logger.info(f"Loading layer {row['Name']}")
        if row["display"] == True:
            if row["file_type"] == "shp":
                gdf = gpd.read_file(Path(row["shp"]))
            elif row["file_type"] == "gdb":
                gdb = Path(row["gdb"])
                gdf = gpd.read_file(gdb, layer=row["layer"])
            else:
                return None

            gdf["color"] = row["color"]
            # gdf["label"] = gdf[row["label"]].astype(str)
            # print(gdf.columns)
            if type(row["label"]) == str:
                gdf["label"] = gdf[row["label"]].astype(str).replace("nan", "")
            else:
                gdf["label"] = ""

            gdf["layer"] = row["Name"]
            gdf["size"] = row["size"]
            # print(row['Name'])
            # print(gdf.crs)

            return gdf[
                ["color", "label", "layer", "size", "geometry"]
            ]  # .to_crs(epsg=4326)
        else:
            logger.info(f"Layer {row['Name']} is not displayed")
            # print(row['Name'])
            return None
    except Exception as e:
        logger.error(f"Layer {row['Name']} failed to load due to {e}")
        return None


# Create gdb
gdfs = {y["Name"]: get_layer(y) for i, y in config.iterrows()}
# gdfs = {y['Name']:y for i,y in config.iterrows()}

# gdfs['Proposed Pipeline']

epsg = 4326
# epsg = 26745
# epsg = 2229
# epsg = 6424
import arrow

gdf = pd.concat([gdf.to_crs(epsg=epsg) for gdf in gdfs.values() if gdf is not None])

gdf.to_parquet(data_path / f"gdf-{arrow.now().format('YYYY-MM-DD')}.parquet")