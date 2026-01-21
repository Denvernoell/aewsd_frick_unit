import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import dotenv
    import os
    import matplotlib.pyplot as plt
    from shapely import wkb as wkb
    import geopandas as gpd
    from pathlib import Path
    import polars as pl

    dotenv.load_dotenv('.env')
    if not os.getenv("md_access"):
        raise ValueError("MotherDuck access token not found in environment variables.")
    con = duckdb.connect(
            f"md:?motherduck_token={os.getenv('md_access')}",
            read_only=False,
        )

    con.sql("USE aewsd")
    con.sql("""
    INSTALL spatial;
    LOAD spatial;
    """)
    epsg = 2229
    return con, epsg, gpd, mo, plt, wkb


@app.cell
def _(con, epsg, gpd, plt, wkb):
    _elements = con.sql("""
        WITH area AS (
            SELECT ST_Union_Agg(geometry) AS geom
            FROM elements
            WHERE layer_name = 'DiGiorgio Service Area'
        ),
        buffered AS (
            SELECT ST_Buffer(geom, 2640) AS buffered_geom
            FROM area
        )
        SELECT ST_AsWKB(e.geometry) AS wkb, e.layer_name, e.properties
        FROM elements e, buffered
        WHERE ST_Within(e.geometry, buffered.buffered_geom)
    """).pl()

    _geometries = [wkb.loads(b) for b in _elements["wkb"].to_list()]
    _gdf = gpd.GeoDataFrame(
        {
            "layer_name": _elements["layer_name"].to_list(),
            "properties": _elements["properties"].to_list(),
        },
        geometry=_geometries,
        crs=f"EPSG:{epsg}",
    )
    _ax = _gdf.plot(column="layer_name", legend=True, alpha=0.7, cmap="tab20")
    _ax.set_title("Elements within DiGiorgio Service Area (0.5 mile buffer)")
    _ax.set_xlabel("Longitude")
    _ax.set_ylabel("Latitude")
    plt.gca()
    return


@app.cell
def _(con, mo):
    dd = mo.ui.dropdown(
        options=[
            "Layer Visualization",
            "Data Summary",
            "Export Data",
            "Map Creation",
            "Spatial Analysis",
        ],
        label="Select Action",
    )

    l_layers = [r[0] for r in con.sql("""
    select distinct("name") from layers
    """).fetchall()]
    s_layer = mo.ui.dropdown(
        options=l_layers,
        label="Select Layer",
    )
    s_layer
    return dd, s_layer


@app.cell
def _():
    import leafmap.maplibregl as leafmap
    # _m = leafmap.Map()
    # _m.add_duckdb_layer(
    #     data=con,
    #     layer_name="elements",
    #     # sql=f"""
    #     # WITH area AS (
    #     #     SELECT ST_Union_Agg(geometry) AS geom
    #     #     FROM elements
    #     #     WHERE layer_name = 'DiGiorgio Service Area'
    #     # ),
    #     # buffered AS (
    #     #     SELECT ST_Buffer(geom, 2640) AS buffered_geom
    #     # )
    #     # SELECT ST_AsWKB(e.geometry) AS wkb, e.layer_name
    #     # FROM elements e, buffered
    #     # WHERE ST_Within(e.geometry, buffered.buffered_geom) AND e.layer_name IN ('{s_layer.value}', 'DiGiorgio Service Area')
    #     # """,
    #     # geometry_column="wkb",
    #     # layer_name=f"Elements in Layer: {s_layer.value}",
    #     # crs=epsg,
    # )
    # # _m
    return (leafmap,)


@app.cell
def _(con, dd, epsg, gpd, leafmap, mo, s_layer, wkb):
    if not s_layer.value:
        mo.ui.alert("Please select a layer to proceed.")
        raise ValueError("No layer selected. Please choose a layer from the dropdown.")

    _layer_name = s_layer.value
    _action = dd.value
    _elements_layer = con.sql(f"""
        WITH area AS (
            SELECT ST_Union_Agg(geometry) AS geom
            FROM elements
            WHERE layer_name = 'DiGiorgio Service Area'
        ),
        buffered AS (
            SELECT ST_Buffer(geom, 2640) AS buffered_geom
            FROM area
        )
        SELECT ST_AsWKB(e.geometry) AS wkb, e.layer_name
        FROM elements e, buffered
        WHERE ST_Within(e.geometry, buffered.buffered_geom) AND e.layer_name IN ('{_layer_name}', 'DiGiorgio Service Area')
    """).pl()
    _geometries_layer = [wkb.loads(b) for b in _elements_layer["wkb"].to_list()]
    _gdf_layer = gpd.GeoDataFrame(
        {
            "layer_name": _elements_layer["layer_name"].to_list(),
        },
        geometry=_geometries_layer,
        crs=f"EPSG:{epsg}",
    )
    _gdf_layer_4326 = _gdf_layer.to_crs(epsg=4326)

    # Split into two layers for styling and legend
    _gdf_selected = _gdf_layer_4326[_gdf_layer_4326["layer_name"] == _layer_name]
    _gdf_service = _gdf_layer_4326[_gdf_layer_4326["layer_name"] == "DiGiorgio Service Area"]

    _m = leafmap.Map()
    _m.add_basemap("Esri.WorldImagery")

    # Add selected layer in blue
    _m.add_gdf(
        _gdf_selected,
        # layer_name=f"{_layer_name}",
        # style={"color": "#1f77b4", "fillColor": "#1f77b4", "fillOpacity": 0.6, "opacity": 0.9},
    )

    # Add service area layer in orange
    _m.add_gdf(
        _gdf_service,
        # layer_name="DiGiorgio Service Area",
        # style={"color": "#ff7f0e", "fillColor": "#ff7f0e", "fillOpacity": 0.4, "opacity": 0.9},
    )

    _m.add_legend(
        title="Layers",
        labels=[_layer_name, "DiGiorgio Service Area"],
        colors=["#1f77b4", "#ff7f0e"],
    )

    _m
    return


if __name__ == "__main__":
    app.run()
