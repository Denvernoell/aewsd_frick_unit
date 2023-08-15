import folium
import leafmap.foliumap as leafmap
import streamlit as st

def make_map(full_gdf,apns,pipes,config):
	df = config
	# get_type = lambda df,shape_type: df.loc[df['shape_type'] == shape_type].iterrows()
	
	non_gdf_layers = [
		'APNs',
		'Proposed Pipeline',
	]
	hidden_gdf_layers = [
		'Frick Unit Service Area',
		'Frick Unit Service Area 2',
		'Groundwater Service Area',
	]
	get_type = lambda df,shape_type: df.loc[
		(df['shape_type'] == shape_type) &
		(~df['Name'].isin(hidden_gdf_layers + non_gdf_layers))
		].iterrows()

	clip_layers = [
		'Proposed Turnout',
		# 'Proposed Pipeline',
		# "Frick Unit Service Area",
		# "AEWSD Alignments",
		]
	service_boundary = full_gdf.pipe(lambda df:df.loc[df['label'] == "Frick Unit North Service Area"])
	intersect = lambda gdf: gdf[gdf.intersects(service_boundary.unary_union)]
	clip = lambda gdf: gdf.clip(service_boundary)
	apns = apns.to_crs("EPSG:4326")
	# find interescting shapes
	# intersecting_apns = apns[apns.intersects(service_boundary.unary_union)]

	m = leafmap.Map(
		# tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
		# attr="Esri",
		google_map="HYBRID",
		min_zoom=3,
		
		# zoom_control=False,
		draw_control=False,
		search_control=False,
	)


	for i,y in get_type(df,"hollow_polygon"):
		layer = y['Name']
		# st.markdown(layer)
		# st.dataframe(y)
		try:
			gdf = full_gdf[full_gdf['layer']==layer]
			if layer in clip_layers:
				gdf = clip(gdf)
				# gdf = intersect(gdf)
			color = gdf['color'].unique()[0]
			# st.dataframe(gdf.drop(columns=['geometry']))
			m.add_gdf(
				gdf,
				# layer=layer,
				fields=['layer'],
				highlight_function=lambda x: {"fillOpacity": 0.7, "weight": 6, "color": "lightgreen"},
				style={
					'color':color,
					'fillColor':"none",
					},
				)
		except Exception as e:
			st.markdown(f"Error with {layer}\n{e}")
			# print(f"Error with {layer}")

	# for layer in filled_polygons:
	for i,y in get_type(df,"filled_polygon"):
		layer = y['Name']
		# st.markdown(layer)
		try:
			gdf = full_gdf[full_gdf['layer']==layer]
			if layer in clip_layers:
				gdf = clip(gdf)
				# gdf = intersect(gdf)
			color = gdf['color'].unique()[0]


			m.add_gdf(
				gdf,
				layer_name=layer,
				# alpha=y['alpha'],
				# highlight_function=lambda x: {"l":x['properties']['label']},
				fields=['layer'],
				highlight_function=lambda x: {"fillOpacity": 0.4, "weight": 6, "color": "lightgreen"},
				style={
					# 'color':color,
					'color':"none",
					'fillColor':color,
					"tooltip":"label",
					"alpha":y['alpha'],
					},
					# tooltip="label",
				zoom_to_layer=True,
				)

		except Exception as e:
			st.markdown(f"Error with {layer}\n{e}")
			# print(f"Error with {layer}")
	
	# intersecting_apns = apns[apns.intersects(service_boundary.unary_union)]
	district_boundary = full_gdf.pipe(lambda df:df.loc[df['layer'] == "District Boundary"])
	intersecting_apns = apns[apns.intersects(district_boundary.unary_union)]
	# st.dataframe(intersecting_apns.drop(columns=['geometry']))
	apn_gdf = intersecting_apns
	# apn_gdf = apns

	apn_gdf['size'] = apn_gdf.geometry.area  
	# apn_gdf = apns
	# st.dataframe(apn_gdf.drop(columns=['geometry']))

	m.add_gdf(
		apn_gdf,
		layer_name="APNs",
		# style_function=lambda x: {"color": "red", "fillOpacity": 0},
		fields=['APN','Acreage','Landowner'],
		# fields=['APN_DASH','ASSR_ACRES','GIS Landowner'],
		# highlight_function=lambda x: {"fillOpacity": 0.7, "weight": 6, "color": "lightgreen"},
		style={
			'color':"white",
			"weight":0.5,
		},
	)
	# for layer in points:
	for i,y in get_type(df,"point"):
		layer = y['Name']
		# st.markdown(layer)
		try:
			gdf = full_gdf[full_gdf['layer']==layer]
			if layer in clip_layers:
				gdf = clip(gdf)
				# intersect(gdf)
			color = gdf['color'].unique()[0]
			for i,y in gdf.iterrows():
				folium.Circle(
					radius=y['size'],
					location=[y.geometry.y,y.geometry.x],
					color=y['color'],
					fill=True,
					# fields=["label"],
					tooltip=f"<b>Layer: </b>{y['layer']}<br><b>Label: </b>{y['label']}",
					).add_to(m)
			# add apns and labels
			
		except:
			st.markdown(f"Error with {layer}")


	# for layer in lines:
	for i,y in get_type(df,"line"):
		layer = y['Name']
		# st.markdown(layer)
		try:
			gdf = full_gdf[full_gdf['layer']==layer]
			# st.markdown(layer)
			# st.markdown(gdf.crs)
			if layer in clip_layers:
				gdf = clip(gdf)
				# intersect(gdf)
			color = gdf['color'].unique()[0]
			m.add_gdf(
				gdf,
				layer_name=layer,
				fields=['layer','label'],
				# line_weight=y['size'],
				highlight_function=lambda x: {"fillOpacity": 0.7, "weight": 6, "color": "lightgreen"},
				# tooltip="label",
				style={
					'color': color,
					'weight':y['size'],
					},
				)


		except Exception as e:
			st.markdown(f"Error with {layer}\n{e}")
	# apns.crs = "EPSG:4326"
	# st.markdown(apns.crs)
	# apn_gdf = clip(apns.to_crs("EPSG:4326"))
	# apn_gdf = clip(apns)
	# apn_gdf = apns.to_crs("EPSG:4326")

	# for i,row in get_type(df,"hollow_polygons"):
	# # for layer in hollow_polygons:
	# 	name = row['Name']
	gdf = pipes
	color = 'orange'
	m.add_gdf(
		gdf,
		layer_name="Proposed Pipeline",
		fields=['layer','label'],
		highlight_function=lambda x: {"fillOpacity": 0.7, "weight": 6, "color": "lightgreen"},
		# tooltip="label",
		style={
			'color': color,
			'weight':4,
			},
		)

	m.add_legend(
		title="Legend",
		legend_dict={
			y['Name']:y['color'] for i,y in config.iterrows() if y['Name'] not in hidden_gdf_layers
		}
	)
	m.zoom_to_gdf(
		full_gdf[full_gdf['layer'] == "Proposed Pipeline"],
	)

	"""
	"""
	# m.fit_bounds(bounds=ll_bounds,max_zoom=12)
	# m.set_max_bounds(ll_bounds)
	return m