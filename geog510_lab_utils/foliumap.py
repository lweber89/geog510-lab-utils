import folium


class Map(folium.Map):

    def __init__(self, center=(0, 0), zoom=2, **kwargs):
        """_summary_

        Args:
            center (tuple, optional): _description_. Defaults to (0, 0).
            zoom (int, optional): _description_. Defaults to 2.
        """
        super().__init__(location=center, zoom_start=zoom, **kwargs)

    def add_geojson(self, data, hover_style=None, **kwargs):
        """_summary_

        Args:
            data (_type_): _description_
            hover_style (_type_, optional): _description_. Defaults to None.
        """

        import geopandas as gpd

        if hover_style is None:
            hover_style = {"color": "green", "fillOpacity": 0.2}

        if isinstance(data, str):
            gdf = gpd.read_file(data)
            geojson = gdf.__geo_interface__

        elif isinstance(data, dict):
            geojson = data

        folium.GeoJson(data=geojson, **kwargs).add_to(self)

    def add_gdf(self, gdf, **kwargs):
        """_summary_

        Args:
            gdf (_type_): _description_
        """

        gdf = gdf.to_crs(epsg=4326)
        geojson = gdf.__geo_interface__

        self.add_geojson(geojson, **kwargs)

    def add_vector(self, data, **kwargs):
        """_summary_

        Args:
            data (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
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
        """_summary_"""
        folium.LayerControl().add_to(self)
