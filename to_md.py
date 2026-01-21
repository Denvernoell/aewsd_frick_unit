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
    from shapely import wkb as _wkb
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

    con.sql("CREATE SCHEMA IF NOT EXISTS aewsd")
    con.sql("USE aewsd")
    con.sql("""
    INSTALL spatial;
    LOAD spatial;
    """)
    return Path, con, gpd, mo, pl, plt


@app.cell
def _(con):
    # create layers table
    con.sql("""
        CREATE TABLE if not exists layers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            shape_type TEXT NOT NULL,
            color TEXT,
            custom_icon TEXT,
            size FLOAT,
            alpha FLOAT,
            label TEXT,
            file_path TEXT NOT NULL,
            layer TEXT,
        )
    """)

    con.sql("""
        CREATE TABLE if not exists elements (
            id INTEGER PRIMARY KEY,
            layer_name TEXT NOT NULL,
            geometry GEOMETRY NOT NULL,
            properties JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.sql("""
        CREATE TABLE if not exists maps (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            district GEOMETRY NOT NULL,
            unit GEOMETRY NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        )
    """)

    con.sql("""
        CREATE TABLE if not exists map_elements (
            id INTEGER PRIMARY KEY,
            map_name TEXT NOT NULL,
            clip_to_district BOOLEAN DEFAULT FALSE,
            clip_to_unit BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        )
    """)
    return


@app.cell
def _(con, pl):

    d_layers = pl.read_excel('data/config.xlsx',sheet_name="Layers")
    for row in d_layers.to_dicts():
        con.sql(f"""
            INSERT INTO layers (id, name, shape_type, custom_icon, color, size, alpha, label, file_path, layer)
            VALUES ({row['id']}, '{row['Name']}', '{row['shape_type']}', '{row['custom_icon']}','{row['color']}', {row['size']}, {row['alpha']}, '{row['label']}', '{row['file_path']}', '{row['layer']}')
        """)
    return (d_layers,)


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM "layers" LIMIT 100
        """,
        engine=con
    )
    return


@app.cell
def _(Path, con, d_layers, gpd):
    epsg = 2229

    _read_options = {
        ".shp": lambda file: gpd.read_file(file),
        ".parquet": lambda file: gpd.read_parquet(file),
    }

    for _row in d_layers.to_dicts()[17:]:
        try:
            file_path = Path(_row["file_path"])
            if file_path.suffix == ".gdb":
                _gdf = gpd.read_file(file_path, layer=_row["layer"])
            else:
                _gdf = _read_options[file_path.suffix](file_path)
    
            _gdf = _gdf.to_crs(epsg=epsg)
            _gdf["properties"] = _gdf.drop(columns="geometry").apply(lambda r: r.to_json(), axis=1)
            _gdf["layer_name"] = _row["Name"]
            _gdf["geometry"] = _gdf["geometry"].apply(lambda geom: geom.wkb)
            _gdf = _gdf[["geometry", "properties", "layer_name"]]
    
            # create incremental ids to satisfy NOT NULL PRIMARY KEY constraint
            _start_id = con.execute("SELECT COALESCE(MAX(id) + 1, 1) FROM elements").fetchone()[0]
            _gdf.insert(0, "id", range(_start_id, _start_id + len(_gdf)))
    
            con.register("gdf", _gdf)
            # add to elements table
            con.sql("""
                INSERT INTO elements (id, layer_name, geometry, properties)
                SELECT id, layer_name, ST_GeomFromWKB(geometry), CAST(properties AS JSON)
                FROM gdf
            """)
        except Exception as e:
            print(f"Error processing layer {_row['Name']}: {e}")
        
    return (epsg,)


app._unparsable_cell(
    r"""
    for sht in [\"Full\",\"Simple\",\"DiGiorgio\"]:
        _df = pl.read_excel('data/config.xlsx',sheet_name=sht)
        con.sql(\"\"\"
                INSERT INTO elements (id, layer_name, geometry, properties)
                SELECT id, layer_name, ST_GeomFromWKB(geometry), CAST(properties AS JSON)
                FROM gdf
            \"\"\")
        for row in _df.to_dicts():
    """,
    name="_"
)


@app.cell
def _(con):
    con.sql("""
    from elements
    SELECT ST_AsWKB(geometry) AS wkb, layer_name, properties
    where layer_name = 'DiGiorgio Service Area'
    """)
    return


@app.cell
def _(con, epsg, gpd, plt):
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

    _geometries = [_wkb.loads(b) for b in _elements["wkb"].to_list()]
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
def _(d_layers, mo):
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

    s_layer = mo.ui.dropdown(
        options=d_layers["Name"].to_list(),
        label="Select Layer",
    )

    return (s_layer,)


@app.cell
def _(s_layer):
    s_layer
    return


@app.cell
def _(con, epsg, gpd, plt, s_layer):
    # if s_layer.value:
    _df = con.sql(f"""
        SELECT ST_AsWKB(geometry) AS wkb, layer_name, properties
        FROM elements
        WHERE layer_name = '{s_layer.value}'
    """).pl()
    _geometries = [_wkb.loads(b) for b in _df["wkb"].to_list()]
    _gdf = gpd.GeoDataFrame(
        {
            "layer_name": _df["layer_name"].to_list(),
            "properties": _df["properties"].to_list(),
        },
        geometry=_geometries,
        crs=f"EPSG:{epsg}",
    )
    _ax = _gdf.plot(column="layer_name", legend=True, alpha=0.7, cmap="tab20")
    _ax.set_title(f"Visualization of Layer: {s_layer.value}")
    _ax.set_xlabel("Longitude")
    _ax.set_ylabel("Latitude")
    plt.gca()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
