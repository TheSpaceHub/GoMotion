import pandas as pd
import barri_manager
from math import sin, cos, pi


def dist(A, B):
    """Returns distance between two coordinates. We approximate the
    length of the geodesic by the distance between the points"""
    R = 6371000  # Earth radius
    f = pi / 180  # Conversion factor
    return R * (
        (
            2
            - 2 * sin(A.x * f) * sin(B.x * f) * cos(A.y * f - B.y * f)
            - 2 * cos(A.x * f) * cos(B.x * f)
        )
        ** 0.5
    )


def create_edge_csv(gdf=None):
    if gdf is None:
        gdf = barri_manager.load_gdf()

    edges = []

    for i, barri in gdf.iterrows():
        intersecting_gdf = gdf[
            gdf["geometria_wgs84"].intersects(barri["geometria_wgs84"])
        ]
        neighbors = intersecting_gdf[intersecting_gdf["codi_barri"] != barri["codi_barri"]]
        b_point = barri["geometria_wgs84"].centroid

        for i, neighbor in neighbors.iterrows():
            n_point = neighbor["geometria_wgs84"].centroid
            edges.append(
                {
                    "barri_a": barri["nom_barri"],
                    "barri_b": neighbor["nom_barri"],
                    "dist": dist(b_point, n_point),
                }
            )

    edge_df = pd.DataFrame(edges)
    edge_df.to_csv("data/barris_edges.csv", index=False)
    
def create_node_csv(gdf = None):
    if gdf is None:
        gdf = barri_manager.load_gdf()
    nodes = []
    for _, barri in gdf.iterrows():
        nodes.append(
            {
                "barri" : barri["nom_barri"],
                "x" : barri["geometria_wgs84"].centroid.x,
                "y" : barri["geometria_wgs84"].centroid.y,
            }
        )
    node_df = pd.DataFrame(nodes)
    node_df.to_csv("data/barris_nodes.csv", index=False)
        
    
def create_csv():
    #wrap both
    gdf = barri_manager.load_gdf()
    create_node_csv()
    create_edge_csv()
