import geopandas as gpd
from pathlib import Path
import pandas as pd
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="INFO")

data_path = Path(
	# "data"
	__file__
	# "G:\Arvin-Edison WSD-1215\121523003-Frick Unit Pipeline\400 GIS\Scripts\aewsd_frick_unit\data"
	).parent
logger.info(f"data_path: {data_path}")

config = pd.read_excel(data_path.joinpath('config.xlsx'), sheet_name='layers').dropna(subset=['display'])

# filter out the following
# df['layer'] == 'Panama Unit Service Area' & df['label'] == 'Frick Unit North Service Area'
# df['layer'] == 'Frick Unit Pipeline' & df['label'] == 'Frick Unit'
# gdf = gpd.read_parquet(data_path.joinpath("gdf-2023-08-15.parquet"))

# grab newest parquet file
gdf_file = sorted(
				data_path.glob("gdf-*.parquet"),
				reverse=True,
				key=lambda x:x.stem)[0]

gdf = gpd.read_parquet(
	gdf_file
	# data_path.joinpath("gdf-2024-01-16.parquet")
	)
logger.log("INFO", f"loaded {gdf_file}")


district_boundary = gdf.pipe(lambda df:df.loc[df['layer'] == "District Boundary"])
# apns = gpd.read_parquet(data_path.joinpath("apns.parquet")).to_crs("EPSG:4326")
# apn_gdf = apns[apns.intersects(district_boundary.unary_union)]

apn_gdf = gpd.read_parquet(data_path.joinpath("apn_gdf_sa.parquet")).to_crs("EPSG:4326")
pipes = gpd.read_parquet(data_path.joinpath("pipes.parquet"))