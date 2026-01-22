import sys
import os



# Get the parent directory of the api folder
api_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(api_dir))
sys.path.insert(0, project_root)
print(f"API directory: {api_dir}")
print(f"Project root: {project_root}")
# sys.path.append("..")
# C:\1-Projects\aewsd_frick_unit\map_parquet.py


from fasthtml.common import *
from fapp import app, rt, logger

import leafmap.foliumap as leafmap
import folium


# from loguru import logger
# import sys
# import leafmap.foliumap as leafmap
# import folium
# # import leafmap.maplibregl as leafmap



# def build_tooltip_html(row, layer_name):
#     """Build custom tooltip HTML from label_list"""
#     tooltip_parts = [f"<b>Layer:</b> {layer_name}"]

#     if 'label_list' in row.index and row['label_list'] is not None:
#         if isinstance(row['label_list'], str):
#             label_fields = [label.strip() for label in row['label_list'].split(',')]

#             # Check if we need to parse properties JSON
#             properties_dict = {}
#             if 'properties' in row.index and row['properties'] is not None:
#                 try:
#                     import json
#                     if isinstance(row['properties'], str):
#                         properties_dict = json.loads(row['properties'])
#                     elif isinstance(row['properties'], dict):
#                         properties_dict = row['properties']
#                 except:
#                     pass

#             for field in label_fields:
#                 value = None
#                 # First check in direct row columns
#                 if field in row.index:
#                     value = row[field]
#                 # Then check in properties dict
#                 elif field in properties_dict:
#                     value = properties_dict[field]

#                 if value is not None and str(value).strip() != '' and str(value) != 'None':
#                     tooltip_parts.append(f"<b>{field}:</b> {value}")

#     return "<br>".join(tooltip_parts)


# def plot_map(full_gdf, config):
#     m = leafmap.Map(
#         google_map="HYBRID",
#         min_zoom=3,
#         zoom=5,
#         # zoom_control=False,
#         draw_control=False,
#         search_control=False,
#     )
#     for i, y in config[:].iterrows():
#         try:
#             gdf = full_gdf[full_gdf["layer"] == y["Name"]]
#             logger.info(y["Name"])

#             if y["shape_type"] == "hollow_polygon":
#                 for idx, row in gdf.iterrows():
#                     tooltip_html = build_tooltip_html(row, y["Name"])
#                     folium.GeoJson(
#                         row.geometry.__geo_interface__,
#                         name=y["Name"],
#                         tooltip=folium.Tooltip(tooltip_html),
#                         style_function=lambda x, color=y["color"], size=y["size"]: {
#                             "color": color,
#                             "fillColor": "none",
#                             "weight": size,
#                         },
#                         highlight_function=lambda x: {
#                             "fillOpacity": 0.7,
#                             "weight": 6,
#                             "color": "lightgreen",
#                         },
#                         ).add_to(m)
#             if y["shape_type"] == "dashed_line":
#                 for idx, row in gdf.iterrows():
#                     tooltip_html = build_tooltip_html(row, y["Name"])
#                     folium.GeoJson(
#                         row.geometry.__geo_interface__,
#                         name=y["Name"],
#                         tooltip=folium.Tooltip(tooltip_html),
#                         dash_array="20",
#                         style_function=lambda x, color=y["color"], size=y["size"]: {
#                             "color": color,
#                             "weight": size,
#                         },
#                         highlight_function=lambda x: {
#                             "fillOpacity": 0.7,
#                             "weight": 6,
#                             "color": "lightgreen",
#                         },
#                     ).add_to(m)

#             if y["shape_type"] == "line":
#                 for idx, row in gdf.iterrows():
#                     tooltip_html = build_tooltip_html(row, y["Name"])

#                     folium.GeoJson(
#                         row.geometry.__geo_interface__,
#                         name=y["Name"],
#                         tooltip=folium.Tooltip(tooltip_html),
#                         style_function=lambda x, color=y["color"], size=y["size"]: {
#                             "color": color,
#                             "weight": size,
#                         },
#                         highlight_function=lambda x: {
#                             "fillOpacity": 0.7,
#                             "weight": 6,
#                             "color": "lightgreen",
#                         },
#                     ).add_to(m)

#             if y["shape_type"] == "filled_polygon":
#                 for idx, row in gdf.iterrows():
#                     tooltip_html = build_tooltip_html(row, y["Name"])

#                     folium.GeoJson(
#                         row.geometry.__geo_interface__,
#                         name=y["Name"],
#                         tooltip=folium.Tooltip(tooltip_html),
#                         style_function=lambda x, color=y["color"], alpha=y["alpha"]: {
#                             "color": color,
#                             "fillColor": color,
#                             "fillOpacity": alpha,
#                             "weight": 0.2,
#                         },
#                         highlight_function=lambda x: {
#                             "fillOpacity": 0.4,
#                             "weight": 6,
#                             "color": "lightgreen",
#                         },
#                     ).add_to(m)

#                 # Zoom to first feature of this layer
#                 if len(gdf) > 0:
#                     bounds = gdf.total_bounds
#                     m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

#             if y["shape_type"] == "point":
#                 for idx, row in gdf.iterrows():
#                     tooltip_html = build_tooltip_html(row, y["Name"])

#                     folium.Circle(
#                         radius=y["size"],
#                         location=[row.geometry.y, row.geometry.x],
#                         color=y["color"],
#                         fill=True,
#                         tooltip=folium.Tooltip(tooltip_html),
#                     ).add_to(m)

#         except Exception as e:
#             logger.error(y["Name"])
#             logger.error(gdf)
#             logger.error(e)

#     hidden_gdf_layers = [
#         # "Groundwater Service Area",
#     ]

#     legend_dict = {
#         y["Name"]: y["color"]
#         for i, y in config.iterrows()
#         if y["Name"] not in hidden_gdf_layers
#     }
#     # sort alphabetically
#     legend_dict = {
#         k: v for k, v in sorted(legend_dict.items(), key=lambda item: item[0])
#     }

#     m.add_legend(
#         title="Legend",
#         legend_dict=legend_dict,
#         # position='bottomleft',
#     )

#     # m.zoom_to_gdf(
#     #     full_gdf[full_gdf["layer"] == "Proposed Pipeline"],
#     # )
#     m.zoom_to_bounds(
#         # [-118.89175177,35.22704989, -118.84254324, 35.25253234]
#         [-118.89,   35.227, -118.84,   35.25]
#         # full_gdf.total_bounds
#     )
#     # m.zoom
#     # f"{full_gdf.loc[full_gdf['layer']=='Proposed Pipeline'].total_bounds}"



#     return m





def build_tooltip_html(row, layer_name):
    """Build custom tooltip HTML from label_list"""
    tooltip_parts = [f"<b>Layer:</b> {layer_name}"]

    if 'label_list' in row.index and row['label_list'] is not None:
        if isinstance(row['label_list'], str):
            label_fields = [label.strip() for label in row['label_list'].split(',')]

            # Check if we need to parse properties JSON
            properties_dict = {}
            if 'properties' in row.index and row['properties'] is not None:
                try:
                    import json
                    if isinstance(row['properties'], str):
                        properties_dict = json.loads(row['properties'])
                    elif isinstance(row['properties'], dict):
                        properties_dict = row['properties']
                except:
                    pass

            for field in label_fields:
                value = None
                # First check in direct row columns
                if field in row.index:
                    value = row[field]
                # Then check in properties dict
                elif field in properties_dict:
                    value = properties_dict[field]

                if value is not None and str(value).strip() != '' and str(value) != 'None':
                    tooltip_parts.append(f"<b>{field}:</b> {value}")

    return "<br>".join(tooltip_parts)

def plot_map(full_gdf, config):
    m = leafmap.Map(
        google_map="HYBRID",
        min_zoom=3,
        zoom=5,
        # zoom_control=False,
        draw_control=False,
        search_control=False,
    )
    for i, y in config[:].iterrows():
        try:
            gdf = full_gdf[full_gdf["layer"] == y["Name"]]
            logger.info(y["Name"])

            if y["shape_type"] == "hollow_polygon":
                for idx, row in gdf.iterrows():
                    tooltip_html = build_tooltip_html(row, y["Name"])
                    folium.GeoJson(
                        row.geometry.__geo_interface__,
                        name=y["Name"],
                        tooltip=folium.Tooltip(tooltip_html),
                        style_function=lambda x, color=y["color"], size=y["size"]: {
                            "color": color,
                            "fillColor": "none",
                            "weight": size,
                        },
                        highlight_function=lambda x: {
                            "fillOpacity": 0.7,
                            "weight": 6,
                            "color": "lightgreen",
                        },
                        ).add_to(m)
            if y["shape_type"] == "dashed_line":
                for idx, row in gdf.iterrows():
                    tooltip_html = build_tooltip_html(row, y["Name"])
                    folium.GeoJson(
                        row.geometry.__geo_interface__,
                        name=y["Name"],
                        tooltip=folium.Tooltip(tooltip_html),
                        dash_array="20",
                        style_function=lambda x, color=y["color"], size=y["size"]: {
                            "color": color,
                            "weight": size,
                        },
                        highlight_function=lambda x: {
                            "fillOpacity": 0.7,
                            "weight": 6,
                            "color": "lightgreen",
                        },
                    ).add_to(m)

            if y["shape_type"] == "line":
                for idx, row in gdf.iterrows():
                    tooltip_html = build_tooltip_html(row, y["Name"])

                    folium.GeoJson(
                        row.geometry.__geo_interface__,
                        name=y["Name"],
                        tooltip=folium.Tooltip(tooltip_html),
                        style_function=lambda x, color=y["color"], size=y["size"]: {
                            "color": color,
                            "weight": size,
                        },
                        highlight_function=lambda x: {
                            "fillOpacity": 0.7,
                            "weight": 6,
                            "color": "lightgreen",
                        },
                    ).add_to(m)

            if y["shape_type"] == "filled_polygon":
                for idx, row in gdf.iterrows():
                    tooltip_html = build_tooltip_html(row, y["Name"])

                    folium.GeoJson(
                        row.geometry.__geo_interface__,
                        name=y["Name"],
                        tooltip=folium.Tooltip(tooltip_html),
                        style_function=lambda x, color=y["color"], alpha=y["alpha"]: {
                            "color": color,
                            "fillColor": color,
                            "fillOpacity": alpha,
                            "weight": 0.2,
                        },
                        highlight_function=lambda x: {
                            "fillOpacity": 0.4,
                            "weight": 6,
                            "color": "lightgreen",
                        },
                    ).add_to(m)

                # Zoom to first feature of this layer
                if len(gdf) > 0:
                    bounds = gdf.total_bounds
                    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

            if y["shape_type"] == "point":
                for idx, row in gdf.iterrows():
                    tooltip_html = build_tooltip_html(row, y["Name"])

                    folium.Circle(
                        radius=y["size"],
                        location=[row.geometry.y, row.geometry.x],
                        color=y["color"],
                        fill=True,
                        tooltip=folium.Tooltip(tooltip_html),
                    ).add_to(m)

        except Exception as e:
            logger.error(y["Name"])
            logger.error(gdf)
            logger.error(e)

    hidden_gdf_layers = [
        # "Groundwater Service Area",
    ]

    legend_dict = {
        y["Name"]: y["color"]
        for i, y in config.iterrows()
        if y["Name"] not in hidden_gdf_layers
    }
    # sort alphabetically
    legend_dict = {
        k: v for k, v in sorted(legend_dict.items(), key=lambda item: item[0])
    }

    m.add_legend(
        title="Legend",
        legend_dict=legend_dict,
        # position='bottomleft',
    )

    # m.zoom_to_gdf(
    #     full_gdf[full_gdf["layer"] == "Proposed Pipeline"],
    # )
    m.zoom_to_bounds(
        # [-118.89175177,35.22704989, -118.84254324, 35.25253234]
        [-118.89,   35.227, -118.84,   35.25]
        # full_gdf.total_bounds
    )
    # m.zoom
    # f"{full_gdf.loc[full_gdf['layer']=='Proposed Pipeline'].total_bounds}"



    return m

@rt("/", methods=["GET"])
def map_page():
    from data import get_config, get_gdf
    # from util.map_utils import plot_map
    # from data import get_config, get_gdf
    sheet_name = "DiGiorgio"
    gdf = get_gdf(sheet_name).fillna('')
    config = get_config(sheet_name)
    # gdf
    # st.dataframe(apns.drop(columns=['geometry']))
    m = plot_map(gdf, config)
    return (
        Title("AEWSD DiGiorgio Unit - Map"),
        H2('Arvin-Edison Water Storage District'),
        H3('DiGiorgio Unit Pipeline Project'),
        # H1("Preliminary", style="text-align:center"),
        NotStr(m.to_html()),
        P("Notes"),
        Ul(
            Li("• The mainline alignment shall be selected to minimize construction constraints and overall project cost."),
            Li("• Turnout locations and pipeline sizes are subject to change depending upon input received from landowners."),
        ),
    )