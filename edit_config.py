import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import geopandas as gpd
    import pandas as pd
    from pathlib import Path
    import sys
    from loguru import logger
    import arrow
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    data_path = Path("data")

    d_layers = pl.read_excel('data/config.xlsx',sheet_name="Layers")
    d_layers
    return Path, arrow, d_layers, data_path, gpd, logger, mo, pd, pl


@app.cell
def _(pl):
    d_simple = pl.read_excel('data/config.xlsx',sheet_name="DiGiorgio")
    d_simple
    return (d_simple,)


@app.cell
def _(gpd):
    roads = gpd.read_file(
        'Z:\GIS_Library\Transportation\Road\CountyRoads.gdb',
        layer='CountyRoads_Kern',
    )
    roads
    return


@app.cell
def _(Path, d_layers, d_simple, data_path, gpd, logger, mo, pd, pl):
    config = pd.read_excel(data_path / "config.xlsx", sheet_name="Layers")


    service_boundary_row = config.pipe(lambda df:df.loc[df['Name'] == "DiGiorgio Service Area"])
    service_boundary = gpd.read_file(Path(service_boundary_row['shp'].values[0])).to_crs(4326)

    intersect = lambda gdf: gdf[gdf.intersects(service_boundary.unary_union)]
    clip = lambda gdf: gdf.clip(service_boundary)



    def get_layer(row):
        meta = row
        row = d_layers.filter(
            pl.col("Name") == meta['Name']
        ).to_dicts()[0]
        try:
            logger.info(f"Loading layer {row['Name']}")
            # if row["display"] == True:
            if row["file_type"] == "shp":
                gdf = gpd.read_file(Path(row["shp"])).to_crs(4326)
            elif row["file_type"] == "gdb":
                gdb = Path(row["gdb"])
                gdf = gpd.read_file(gdb, layer=row["layer"]).to_crs(4326)
            else:
                return None

            gdf["color"] = row["color"]
            if type(row["label"]) == str:
                gdf["label"] = gdf[row["label"]].astype(str).replace("nan", "")
            else:
                gdf["label"] = ""

            gdf["layer"] = row["Name"]
            gdf["size"] = row["size"]
            # print(row['Name'])
            # print(gdf.crs)
            if meta['clip_to_unit']:
                gdf = clip(gdf)
            # if row['Name'] == 'Panama Unit Service Area':
            # 	gdf = gdf.loc[gdf['label'] != 'Frick Unit North Service Area']
            # if row['Name'] == 'Panama Unit Pipeline':
            # 	gdf = gdf.loc[gdf['label'] != 'Frick Unit']

            return gdf[
                ["color", "label", "layer", "size", "geometry"]
            ]  # .to_crs(epsg=4326)
            # else:
            #     logger.info(f"Layer {row['Name']} is not displayed")
            #     # print(row['Name'])
            #     return None
        except Exception as e:
            logger.error(f"Layer {row['Name']} failed to load due to {e}")
            mo.md(f"Layer {row['Name']} failed to load due to {e}")
            return f"Layer {row['Name']} failed to load due to {e}"


    # Create gdb
    gdfs = {
        y["Name"]: get_layer(y) for y in d_simple.to_dicts()
        # if y['Name'] == "Roads"
    }
    gdfs
    # [y['Name'] for y in d_simple.to_dicts()]
    return (gdfs,)


@app.cell
def _(gdfs):
    gdfs['Roads']
    return


@app.cell
def _(arrow, data_path, gdfs, pd):

    epsg = 4326
    # epsg = 26745
    # epsg = 2229
    # epsg = 6424

    gdf = pd.concat([gdf.to_crs(epsg=epsg) for gdf in gdfs.values() if gdf is not None])

    gdf.to_parquet(data_path / f"DiGiorgio-{arrow.now().format('YYYY-MM-DD')}.parquet")
    # [type(i) for i in gdfs.values()]
    return


if __name__ == "__main__":
    app.run()
