import geopandas as gpd
import pandas as pd
from shapely import wkt

def load_gdf():
    """Returns the geospacial data of the neighborhoods"""
    
    #load csv
    df = pd.read_csv("data/barris.csv")
    
    #build gdf
    df["geometria_wgs84"] = df["geometria_wgs84"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometria_wgs84")
    gdf = gdf.set_crs("EPSG:4326")
    
    return gdf

def get_barri(point, gdf = None):
    """Returns the neighborhood that cointains a given point"""

    #uses shapely.geometry.Point(x, y) with the coordinates
    if gdf is None:
        gdf = load_gdf()
    match = gdf[gdf.contains(point)]
    try:
        return match["nom_barri"].iloc[0]
    except:
        return None