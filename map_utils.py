import folium
import leafmap.foliumap as leafmap
def make_map(full_gdf):
	lines = ['Proposed Pipeline', 'AEWSD North Canal', 'FFPPP Discharge Pipeline',"AEWSD Alignments"]
	filled_polygons = ['Frick Unit Service Area']
	hollow_polygons = ['District Boundary']
	points = ['Proposed Turnout']

	clip_layers = ['Proposed Turnout', 'Proposed Pipeline',"Frick Unit Service Area","AEWSD Alignments"]
	service_boundary = full_gdf.pipe(lambda df:df.loc[df['label'] == "Frick Unit North Service Area"])
	clip = lambda gdf: gdf.clip(service_boundary)
		
	m = leafmap.Map(
		# tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
		# attr="Esri",
		google_map="HYBRID",
		min_zoom=3,
		# max_zoom=12,

		# min_lat=bounds[2],
		# max_lat=bounds[3],
		# min_lon=bounds[0],
		# max_lon=bounds[1],
		# max_bounds=True,
		
		# zoom_control=False,
		draw_control=False,
		search_control=False,

	)

	for layer in hollow_polygons:
		gdf = full_gdf[full_gdf['layer']==layer]
		if layer in clip_layers:
			gdf = clip(gdf)
		color = gdf['color'].unique()[0]
		m.add_gdf(
			gdf,
			layer_name=layer,
			style={
				'color':color,
				'fillColor':"none",
				},
			)

	for layer in filled_polygons:
		gdf = full_gdf[full_gdf['layer']==layer]
		if layer in clip_layers:
			gdf = clip(gdf)
		color = gdf['color'].unique()[0]
		m.add_gdf(
			gdf,
			layer_name=layer,
			style={
				# 'color':color,
				'color':"none",
				'fillColor':color,
				"tooltip":"label",
				},
				# tooltip="label",
			zoom_to_layer=True,
			)

	for layer in lines:
		gdf = full_gdf[full_gdf['layer']==layer]
		if layer in clip_layers:
			gdf = clip(gdf)
		color = gdf['color'].unique()[0]
		m.add_gdf(
			gdf,
			layer_name=layer,
			# tooltip="label",
			style={'color': color},
			)

	for layer in points:
		gdf = full_gdf[full_gdf['layer']==layer]
		if layer in clip_layers:
			gdf = clip(gdf)
		color = gdf['color'].unique()[0]
		for i,y in gdf.iterrows():
			folium.Circle(
				radius=30,
				location=[y.geometry.y,y.geometry.x],
				color=y['color'],
				fill=True,
				# tooltip=[y["label"]],
				tooltip="Proposed Turnout",
				).add_to(m)
	m.add_legend(
		title="Legend",
		legend_dict={
			"Proposed Pipeline": "orange",
			# "AEWSD Alignments": "orange",
			"AEWSD North Canal": "#0000ff",
			"FFPPP Discharge Pipeline": "red",
			"Frick Unit Service Area": "salmon",
			"District Boundary": "#000000",
			"Proposed Turnout": "#ffff00",
		}
	)


	# m.fit_bounds(bounds=ll_bounds,max_zoom=12)
	# m.set_max_bounds(ll_bounds)
	return m
# filtered_gdf = gdf.clip(bounds)
# filtered_gdf = gdf.clip(bounds)
# m = make_map(gdf)
# m.to_streamlit()