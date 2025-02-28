import os
import json
import asyncio
import aiofiles
import threading
import tempfile
import logging
from typing import Tuple, Union, List, Dict
from shapely.geometry import LineString
from database import insert_geojson_linestring_into_befahrungen
# Overall: we are using geojson file to get the bounding box of the area and then we are using the bounding box to get the data from overpass-api 
# Overpass api supports filtering and different file formas, we are alsoround decimals and use only highways and building edge, data returned with info about nodes 


# TODO: Deprecated code with chunking file and multithreading
# def get_file_size_mb(file_path: str) -> float:
#     """Get file size in MB."""
#     return os.path.getsize(file_path) / (1024 * 1024)


class GeoJSONHandler:
    @staticmethod
    async def sort_data_and_save_file(data: Dict[str, List], filename:str) -> List[Dict]:
        """Sort GeoJSON features asynchronously and save into file."""
        
        # Sorting is CPU-bound → Run it in a thread
        features_sorted = await asyncio.to_thread(
            sorted, data["features"], key=lambda x: x["properties"]["gps_index"]
        )

        geojson_data = {
            "type": "FeatureCollection",
            "name": "Befahrung1",
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
            },
            "features": features_sorted,
        }

        # Create temp file 
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        output_file_path =  os.getcwd() + os.sep + "data" + os.sep + filename
        output_file_path = output_file_path.replace(".geojson", "_sorted.geojson")
        temp_file.close() 
        
        # aiofiles
        async with aiofiles.open(output_file_path, mode="w", encoding="utf-8") as file:
            await file.write(json.dumps(geojson_data, indent=1, separators=(",", ":"), ensure_ascii=False))
        return features_sorted

    @staticmethod
    async def process_data(data: Dict, filename: str) -> None:
        """Process GeoJSON file asynchronously."""
        features_sorted = await GeoJSONHandler.sort_data_and_save_file(data, filename)
        await GeoJSONHandler.create_linestring_from_features_sorted(features_sorted)

    @staticmethod
    async def create_linestring_from_features_sorted(features_sorted: Dict[str, List]) -> None:
        # blocking operation?
        line_string_list = [elem["geometry"]["coordinates"] for elem in features_sorted]
        line_string = LineString(line_string_list)
        await insert_geojson_linestring_into_befahrungen(line_string)


