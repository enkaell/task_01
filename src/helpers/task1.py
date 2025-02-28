import os
import json
import threading
import tempfile
from heapq import merge
import wget
import requests
import urllib.parse
import logging
from typing import Tuple, Union, List
from dataclasses import dataclass
from shapely.geometry import Point, LineString
# Overall: we are using geojson file to get the bounding box of the area and then we are using the bounding box to get the data from overpass-api 
# Overpass api supports filtering and different file formas, we are alsoround decimals and use only highways and building edge, data returned with info about nodes 


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


OSM_FILE_NAME = "OSM-Straßennetzes"
# Request to overpass-api
@dataclass
class Links:
    BaseURL: str = "https://overpass-api.de/api/interpreter?data="
    Body: str = (
        "[out:json];"
        "way['highway']({min_y},{min_x},{max_y},{max_x});"
        "out geom;"
    )
    Encoded : str = ""



def find_coordinate_boundaries(input_file_path: str) -> Tuple[float, float, float, float]:
    try:
        f = open(input_file_path, "r")
    except Exception as e:
        logging.error(f"Error opening file: {e}")
        exit(1)
    with f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            returne
        min_x, max_x = 181 , -181 # Longitude east and longitude west 
        max_y, min_y = -91 , 91 # Latitude north and latitude south
        for record in data["features"]:
            record_x = record["geometry"]["coordinates"][0]
            record_y = record["geometry"]["coordinates"][1]
            if record_x > max_x:
                max_x = record_x
            if record_x < min_x:
                min_x = record_x
            if record_y > max_y:
                max_y = record_y
            if record_y < min_y:
                min_y = record_y
        f.close()
        # We don't loose points during round process because 6 decimal places equal to 111 mm accuracy
        min_x, max_x, min_y, max_y = map(lambda num: round(num, 6), [min_x, max_x, min_y, max_y])
        return min_x, max_x, min_y, max_y

def download_edges_file_from_overpass_api(input_file_path:str, osm_file_path:str):
    # Handling errors? 
    min_x, max_x, min_y, max_y = find_coordinate_boundaries(input_file_path=input_file_path)

    Links.Body = Links.Body.format(min_y=min_y, min_x=min_x, max_y=max_y, max_x=max_x)
    Links.Encoded = Links.BaseURL + urllib.parse.quote(Links.Body)
    print(Links.Encoded)
    wget.download(Links.Encoded, out=osm_file_path)
    logging.info("OSM file downloaded: "+ osm_file_path)



def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)

def sort_geojson_file(file_path: str) -> str:
    """Sort a GeoJSON feature file based on a key."""
    with open(file_path, "r", encoding="utf-8") as f:
        features = json.load(f)
    print(features["features"][0])
    features_sorted = sorted(features["features"], key=lambda x: x["properties"]["gps_index"])
    sorted_file = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".json")
    geojson_data = {
    "type": "FeatureCollection",
    "name": "Befahrung1",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
    "features": features_sorted
    }
    json.dump(geojson_data, sorted_file, indent=1, separators=(",", ":"), ensure_ascii=False)
    sorted_file.close()
    return sorted_file.name


def process_geojson(file_path: str, output_path: str) -> None:
    """Main function to process GeoJSON file, works with big datasets using chunking and multithreading.
        Args: 
            file_path: Path to input GeoJSON 
            output_path: Path to output sorted GeoJSON 
    """
    file_size_mb = get_file_size_mb(file_path)
    logging.info(f"File size: {file_size_mb:.2f} MB")

    if file_size_mb <= 1:
        logging.info("File is small enough to sort in memory.")
        sorted_file = sort_geojson_file(file_path)
        os.rename(sorted_file, output_path)
        return
    else:
        "Extra logic for big files chunking in multithreads"
        return 

def create_lifestring_file_from_sorted(file_path: str) -> None:
    linestring_array = []
    # with open(file_path, "r") as f:
    #     data = json.load(f)
    # for i in range(len(data["features"])-1):
    #     linestring_array.append(LineString([data["features"][i]["geometry"]["coordinates"],  data["features"][i+1]["geometry"]["coordinates"]]).wkt)
    # with open(file_path.removesuffix("_sorted.geojson") + "_linestring.json", "w") as f:
    #     json.dump({"Befahrungen":linestring_array}, f, indent=1, separators=(",", ":"), ensure_ascii=False)
    with open(file_path, "r") as f:
        data = json.load(f)
    for i in range(len(data["features"])):
        coordinates.append([data["features"][i]["geometry"]["coordinates"]])
    with open(file_path.removesuffix("_sorted.geojson") + "_linestring.json", "w") as f:
        json.dump({
            "type": "FeatureCollection",
            "features": [
                {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates":coordinates
                    }
                }
                ]
                }, f, indent=1, separators=(",", ":"), ensure_ascii=False)


def main():
    # Example usage
    input_geojson = "Befahrung1.geojson"
    input_file_path = os.getcwd() + os.sep + "data" + os.sep + input_geojson
    sorted_file_path = input_file_path.replace(".geojson", "_sorted.geojson")
    if not os.path.isfile(sorted_file_path):
        process_geojson(input_file_path, sorted_file_path)
        logging.info(f"Sorted file saved: {sorted_file_path}")
    else:
        logging.info(f"Sorted file already exists: {sorted_file_path}")
    

    osm_file_path =  os.getcwd() + os.sep + "data" + os.sep + OSM_FILE_NAME+"_"+input_geojson.removesuffix(".geojson")+".json"
    if not os.path.isfile(osm_file_path):
        download_edges_file_from_overpass_api(input_file_path, osm_file_path)   
        logging.info(f"OSM file downloaded: {osm_file_path}") 
    else:    
        logging.info(f"OSM file already exists: {osm_file_path}")
    create_lifestring_file_from_sorted(sorted_file_path)


if __name__ == "__main__":
    main()

#  https://overpass-api.de/api/map?bbox=6.2248923, 51.3705417, 6.4317925, 51.4772337

# We need both highway and building data with all the node connections geom -flag
#[out:json];
# (
#   way["highway"](51.3705417, 6.2248923, 51.4772337, 6.4317925);
#   way["building"](51.3705417, 6.2248923, 51.4772337, 6.4317925);
# );
# out count;