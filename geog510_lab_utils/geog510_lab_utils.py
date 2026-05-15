"""Extension of ipyleaflet class Map for custom use in geog510_lab_utils"""

import os
import ipyleaflet
import ipywidgets as widgets


class Map(ipyleaflet.Map):
    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        """Initialize class Map based on ipyleaflet class Map

        Args:
            center (list, optional): Initial center of map. Defaults to [20, 0].
            zoom (int, optional): Initial zoom level of map. Defaults to 2.
            height (str, optional): Initial height of map (in pixels). Defaults to "600px".
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height

    def add_basemap(self, basemap="OpenTopoMap"):
        """Adds basemap to Map based on user input.

        Args:
            basemap (str, optional): Basemap. Defaults to "OpenTopoMap".
        """

        url = eval(f"ipyleaflet.basemaps.{basemap}").build_url()
        layer = ipyleaflet.TileLayer(url=url, name=basemap)
        self.add_layer(layer)

    def add_geojson(self, data, hover_style=None, **kwargs):
        """_summary_Adds GeoJson to map.

        Args:
            data (_type_): Data dictionary representing a GeoJson file
            hover_style (_type_, optional): Initial hover style of Map. Defaults to None.
        """

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
        """Adds GeoDataFrame to Map.

        Args:
            gdf (_type_): Represents GeoDataFrame.
        """

        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__

        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        """Adds any vector data type supported by GeoPandas to the Map.

        Args:
            data (_type_): Any supported data type represented by a file path or a URL.

        Raises:
            ValueError: Provides error if data type is not supported.

        Returns:
            _type_: Breaks from if/elif if GeoJson is provided upon initialization.
        """
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
        """Add layer control to Map"""
        control = ipyleaflet.LayersControl(position="topright")
        self.add_control(control)

    def add_raster(self, data_path, name="Raster Layer", colormap=None, opacity=1):
        """Adds a Cloud Optimized GeoTIFF (COG) or local raster to the map.

        Args:
            data_path (str): The local path or remote URL to the raster file.
            name (str, optional): The name to display in the Layer Control.
                Defaults to 'Raster Layer'.
            colormap (str or dict, optional): The rio-tiler registered colormap
                name (e.g., 'viridis', 'terrain') or a dictionary mapping
                values to colors. Defaults to None.
            opacity (int, optional):The transparency of the layer from 0 to 1.
                Defaults to 1
        """

        from localtileserver import TileClient, get_leaflet_tile_layer

        client = TileClient(data_path)

        tile_layer = get_leaflet_tile_layer(
            client, name=name, colormap=colormap, opacity=opacity
        )

        self.add(tile_layer)
        self.center = client.center()
        self.zoom = client.default_zoom
