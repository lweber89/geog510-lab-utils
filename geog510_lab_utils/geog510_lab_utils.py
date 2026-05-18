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

        self.add_basemap("OpenStreetMap")

    def add_basemap(self, basemap="OpenTopoMap"):
        """Adds basemap to Map based on user input.

        Args:
            basemap (str, optional): Basemap. Defaults to "OpenTopoMap".
        """
        import ipyleaflet

        # 1. Start at the top-level basemaps module
        bm_object = ipyleaflet.basemaps

        # 2. Safely traverse nested names (e.g., "Esri.WorldImagery" -> ["Esri", "WorldImagery"])
        for part in basemap.split("."):
            if hasattr(bm_object, part):
                bm_object = getattr(bm_object, part)
            else:
                raise ValueError(
                    f"Basemap component '{part}' from '{basemap}' not found."
                )

        # 3. Determine how to pull the URL depending on what kind of object it is
        if hasattr(bm_object, "build_url"):
            # It's a direct basemap layer (e.g., Esri.WorldImagery or OpenTopoMap)
            url = bm_object.build_url()
        elif hasattr(bm_object, "Mapnik") and hasattr(bm_object.Mapnik, "build_url"):
            # It's a bundle like OpenStreetMap, fallback to its default style
            url = bm_object.Mapnik.build_url()
        else:
            # Fallback: grab the first available sub-style in the bundle
            try:
                first_style = list(bm_object.values())[0]
                url = first_style.build_url()
            except (AttributeError, IndexError):
                raise AttributeError(
                    f"Could not extract a valid URL from basemap '{basemap}'."
                )

        # 4. Create and add the layer to the map
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

    def add_raster(
        self, data_path, name="Raster Layer", colormap=None, opacity=1, **kwargs
    ):
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
            client, name=name, colormap=colormap, opacity=opacity, **kwargs
        )

        self.add(tile_layer)
        self.center = client.center()
        self.zoom = client.default_zoom

    def add_image(self, image, bounds, **kwargs):
        """Add static image to Map

        Args:
            image (str): URL or filename of image
            bounds (tuple): A tuple of two coordinate tuples:
                ((south_lat, west_lon), (north_lat, east_lon)).
            opacity (float): Opacity value
        """
        from ipyleaflet import ImageOverlay

        overlay = ImageOverlay(url=image, bounds=bounds, **kwargs)

        self.add(overlay)

    def add_video(self, video, bounds, **kwargs):
        """Add video to Map

        Args:
            video (str): URL or filename of video
            bounds (list): A list of two coordinate lists
                [[south_lat, west_lon], [north_lat, east_lon]].
        """
        from ipyleaflet import VideoOverlay

        overlay = VideoOverlay(url=video, bounds=bounds, **kwargs)

        self.add(overlay)

    def add_wms_layer(
        self, url, layers, format="image/png", transparent=True, **kwargs
    ):
        """Adds a WMS layer to the map.

        Args:
            url (str): The WMS service URL.
            layers (str): The layers to display.
            **kwargs: Additional keyword arguments for the ipyleaflet.WMSLayer layer.
        """
        layer = ipyleaflet.WMSLayer(
            url=url, layers=layers, format=format, transparent=transparent, **kwargs
        )
        self.add(layer)

    def add_basemap_gui(self, position="topright"):
        """Adds a basemap chooser to the map.

        Args:
            position (str, optional): Defaults to "topright".
        """
        import ipywidgets as widgets
        from ipyleaflet import WidgetControl
        from IPython.display import display

        # Initialize widget components

        # button

        btn = widgets.Button(icon="map", button_style="success")
        btn.layout.width = "35px"

        # dropdown

        dropdown = widgets.Dropdown(
            options=[
                "OpenStreetMap",
                "OpenTopoMap",
                "Esri.WorldImagery",
                "Esri.NatGeoWorldMap",
                "CartoDB.Positron",
                "CartoDB.DarkMatter",
            ],
            value="OpenStreetMap",
            description="Basemap:",
            style={"description_width": "initial"},
        )
        dropdown.layout.width = "350px"

        # Create a container (HBox) for the widget components
        hbox = widgets.HBox([btn])

        def on_button_clicked(b):
            # Check the current state

            if b.button_style == "success":
                b.button_style = "danger"
                b.icon = "times"
                hbox.children = [dropdown, btn]

            else:
                b.button_style = "success"
                b.icon = "map"
                hbox.children = [btn]

        btn.on_click(on_button_clicked)

        def on_dropdown_change(change):
            if change["new"]:

                basemap_names = dropdown.options

                layers_to_remove = [
                    layer
                    for layer in self.layers
                    if getattr(layer, "name", None) in basemap_names
                ]

                for layer in layers_to_remove:
                    self.remove_layer(layer)

                # 4. Add the new one
                self.add_basemap(change["new"])

        dropdown.observe(on_dropdown_change, names="value")

        # Create a control, position it and add to map
        control = ipyleaflet.WidgetControl(widget=hbox, position=position)
        self.add(control)
