import geopandas as gpd
import pandas as pd
from shapely import wkt
import networkx as nx
import matplotlib.pyplot as plt
from geopy.distance import geodesic


def load_gdf() -> gpd.GeoDataFrame:
    """Returns the geospacial data of the neighborhoods"""

    # load csv
    df = pd.read_csv("data/barris.csv")

    # build gdf
    df["geometria_wgs84"] = df["geometria_wgs84"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometria_wgs84")
    gdf = gdf.set_crs("EPSG:4326")

    return gdf


def get_barri(point, gdf=None) -> str | None:
    """Returns the neighborhood that cointains a given point"""

    # uses shapely.geometry.Point(x, y) with the coordinates
    if gdf is None:
        gdf = load_gdf()
    match = gdf[gdf.contains(point)]
    try:
        return match["nom_barri"].iloc[0]
    except:
        return None


def create_graph(draw=False) -> nx.Graph:
    """Creates a Graph where nodes are neighbourhoods and
    edges exist if neighbourhoods are adjacent"""

    G = nx.Graph()
    gdf = load_gdf()
    gdf["rep_point"] = gdf.geometry.representative_point()

    for row in gdf.itertuples():
        G.add_node(
            row.nom_barri, codi_barri=row.codi_barri
        )  # Node attributes: nom_barri and codi_barri

    sindex = gdf.sindex  # Create spatial index

    for i, barri in gdf.geometry.items():
        candidates = list(
            sindex.intersection(barri.bounds)
        )  # Intersection aproximation using bounding boxes
        for j in candidates:
            if i < j and barri.intersects(
                gdf.geometry[j]
            ):  # Check for exact intersections

                point_i, point_j = gdf.at[i, "rep_point"], gdf.at[j, "rep_point"]
                dist = geodesic((point_i.y, point_i.x), (point_j.y, point_j.x)).meters

                # e: euclidian distance between neighbourhoods, n: flow between neighbourhoods, c: flow capacity
                G.add_edge(
                    gdf.at[i, "nom_barri"],
                    gdf.at[j, "nom_barri"],
                    weight=dist,
                    n=0,
                    c=0,
                )

    # Visualization, can be deleted
    if draw:
        ax = gdf.plot(figsize=(10, 10), color="lightgrey", edgecolor="black")
        gdf["rep_point"].plot(ax=ax, color="red", markersize=30)
        pos = {
            row.nom_barri: (row.rep_point.x, row.rep_point.y)
            for row in gdf.itertuples()
        }
        nx.draw(
            G,
            pos=pos,
            with_labels=False,
            node_size=0,
            node_color="lightblue",
            font_size=6,
        )
        plt.show()
    return G
