"""Main module."""

import ipyleaflet


class Map(ipyleaflet.Map):
    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height

    def add_basemap(self, basemap="OpenTopoMap"):

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add_layer(layer)

    def add_geojson(self, data, hover_style=None, **kwargs):

        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "green", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__

        elif isinstance(data, dict):
            geojson = data

        layer = ipyleaflet.GeoJSON(data=geojson, hover_style=hover_style, **kwargs)
        self.add_layer(layer)

    def add_gdf(self, gdf, **kwargs):

        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__

        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        import geopandas as gpd

        if isinstance(data, str):
            gdf = gpd.read_file(data)

        elif isinstance(data, gpd.GeoDataFrame):
            gdf = data

        elif isinstance(data, dict):
            return self.add_geojson(data, **kwargs)

        else:
            raise ValueError("Invalid data type.")

        self.add_gdf(gdf, **kwargs)

    def add_layer_control(self):
        control = ipyleaflet.LayersControl(position="topright")
        self.add_control(control)
