import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import geopandas as gpd
    from pathlib import Path
    import pandas as pd
    owners_path = r'G:\Arvin-Edison WSD-1215\121525005-DiGiorgio Unit Ph2b-5\400 GIS\Map\AEWSD_DiGiornio_Unit_Landowners\AEWSD_DiGiornio_Unit_Landowners.gdb'
    gpd.list_layers(owners_path)
    return gpd, owners_path


@app.cell
def _(gpd, owners_path):
    g_apns = gpd.read_file(
        owners_path,
        layer='Landowner_Parcels',
    )
    g_apns.plot()
    return (g_apns,)


@app.cell
def _(g_apns):
    g_apns
    return


@app.cell
def _(gpd):
    gpd.read_file(r'G:\Arvin-Edison WSD-1215\121519005-DiGiorgio Unit\GIS\Feature\DiGiorgio_Unit\Pipeline_phases_2024_0521.shp').plot()

    return


@app.cell
def _():
    # gdf = gpd.read_file(

    #     r"Z:\GIS_Library\County\Kern\Kern_Parcels_Owners.shp",
    #     # bbox=service_boundary.total_bounds,
    # 	bbox=service_boundary,
    # ).rename(columns={
    #     "APN": "APN_number",
    #     "APN_LABEL": "APN",
    #     "SHAPE_ACRE": "Acreage",
    #     "ASSE_NAME": "GIS Landowner",
    # })
    return


if __name__ == "__main__":
    app.run()
