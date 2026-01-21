import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import geopandas as gpd
    import pandas as pd
    from pathlib import Path
    import sys
    from loguru import logger
    import arrow
    import marimo as mo
    import duckdb


    # sys.path.append("..")
    from data import get_config

    data_path = Path("data")

    logger.remove()
    logger.add(sys.stderr, level="INFO")
    return Path, arrow, data_path, get_config, gpd, logger, mo, pd


@app.cell
def _(get_config):
    config = {
    	"Full": get_config("Full"),
    	# "Simple": get_config("Simple"),
    	"DiGiorgio": get_config("DiGiorgio"),
    }
    return (config,)


@app.cell
def _(data_path, mo, pd):
    layers = pd.read_excel(
        data_path/"config.xlsx",
        sheet_name="Layers",
    )
    name = mo.ui.dropdown(
        layers['Name'].unique()
    )
    name
    return layers, name


@app.cell
def _(Path, gpd, layers, mo, name):
    def get_gdf(row):
        try:
            # logger.info(f"Loading layer {row['Name']}")
            file_path = Path(row["file_path"])
            read_options = {
                ".shp": lambda file: gpd.read_file(file),
                ".gdb": lambda file: gpd.read_file(file, layer=row["layer"]),
                ".parquet": lambda file: gpd.read_parquet(file),
            }
            # logger.info(file_path)
            gdf = read_options[file_path.suffix](file_path).to_crs(epsg=2229)
            if type(row['filter']) != float:
                # return type(row['filter'] )
                gdf = gdf.query(row['filter'])
            return gdf
        except Exception as e:
            return mo.md(fr"{e}\n\n{row}")


    row = layers.loc[
        layers['Name'] == name.value
    ].iloc[0]


    # get_gdf(row)
    get_gdf(row)
    return


@app.cell
def _():
    # get_gdf(row).plot(
    #     column=row['label'],
    #     legend=True,
    #     # title=row['Name'],
    #     legend_kwds={
    #         "bbox_to_anchor":(1, 0.5)
    #     }
    # )
    return


@app.cell
def _(gpd, layers):
    gpd.read_file(
        layers.loc[layers["Name"] == "Existing Service Area"]["file_path"].iloc[0]
    ).total_bounds
    return


@app.cell
def _(Path, gpd, layers, logger):
    district_boundary = gpd.read_file(
        layers.loc[layers["Name"] == "District Boundary"]["file_path"].iloc[0]
    )
    service_boundary = gpd.read_file(
        layers.loc[layers["Name"] == "Existing Service Area"]["file_path"].iloc[0]
    )

    intersect = lambda gdf: gdf[gdf.intersects(service_boundary.unary_union)]
    clip = lambda gdf: gdf.clip(service_boundary)


    def get_layer(row, sheet_name):
        try:
            # logger.info(f"Loading layer {row['Name']}")
            file_path = Path(row["file_path"])
            read_options = {
                ".shp": lambda file: gpd.read_file(file),
                ".gdb": lambda file: gpd.read_file(file, layer=row["layer"]),
                ".parquet": lambda file: gpd.read_parquet(file),
            }
            # logger.info(file_path)
            gdf = read_options[file_path.suffix](file_path).to_crs(epsg=2229)

            # if row["Name"] == "APNs":
            #     if sheet_name == "Full":
            #         gdf["label"] = (
            #             gdf["label"] + "\nService Area Type: " + gdf["Service Area Type"]
            #         )
            #     gdf["label"] = gdf["label"].str.replace(r"\n", "<br>", regex=True)

            # if row["Name"] == "Panama Unit Pipeline":
            #     gdf = gdf.loc[gdf["Name"] != "Frick Unit"]

            gdf["color"] = row["color"]
            gdf["layer"] = row["Name"]
            gdf["size"] = row["size"]

            gdf['label_list'] = row['label_list']

            if type(row["label"]) == str:
                gdf["label"] = gdf[row["label"]].astype(str).replace("nan", "")
            else:
                gdf["label"] = ""
            gdf["properties"] = gdf.drop(columns="geometry").apply(lambda r: r.to_json(), axis=1)

            if row["clip_to_unit"] == True:
                logger.info(f"Clipping layer {row['Name']}")
                gdf = clip(gdf)
            if type(row['filter']) != float:
                # return type(row['filter'] )
                gdf = gdf.query(row['filter'])
            logger.info(list(gdf.columns))

            return gdf[
                [
                    "color",
                    "label", 
                    "layer",
                    "size",
                    'properties',
                    'label_list',
                    "geometry"
                ]
            ] 
            # .to_crs(epsg=4326)
        except Exception as e:
            logger.error(f"Layer {row['Name']} failed to load due to {e}")
            # logger.error(gdf.columns)
            return None
    return (get_layer,)


@app.cell
def _(arrow, config, data_path, get_layer, pd):
    def get_sheet(sheet_name):
        gdfs = {y["Name"]: get_layer(y, sheet_name) for i, y in config[sheet_name].iterrows()}
        epsg = 4326
        gdf = pd.concat([gdf.to_crs(epsg=epsg) for gdf in gdfs.values() if gdf is not None])
        gdf.to_parquet(
            data_path / f"{sheet_name}-{arrow.now().format('YYYY-MM-DD')}.parquet"
        )


    # get_sheet("Full")
    # get_sheet("Simple")
    get_sheet("DiGiorgio")
    return


@app.cell
def _():
    # https://www.arcgis.com/home/item.html?id=3990a3cd8c194be1a62fb91620a44c03#data
    # https://gisdata.in.gov/server/rest/services/Hosted/CONTOURS_24K_USGS_IN/FeatureServer/53
    return


if __name__ == "__main__":
    app.run()
