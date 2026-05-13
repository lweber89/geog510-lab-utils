import folium


class Map(folium.Map):

    def __init__(self, center=(0, 0), zoom=2, **kwargs):
        folium.LayerControl().add_to(self)
