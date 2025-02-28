import os
import json
import asyncio
import aiohttp
import urllib.parse
import logging
from typing import List, Dict
from dataclasses import dataclass
from config import ACCURACY
from database import insert_osm_json_linestring_into_kanten
from models import OSMtoDBModel
from shapely.geometry import LineString


# Request to overpass-api
@dataclass
class Links:
    BaseURL: str = "https://overpass-api.de/api/interpreter?data="
    Body: str = (
        "[out:json];"
        "way['highway']({min_y},{min_x},{max_y},{max_x});"
        "out geom;"
    )
    Encoded: str = ""

class AsyncOSMDataIterator:
    def __init__(self, elements: List[Dict]):
        self.elements = elements
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.elements):
            raise StopAsyncIteration
        elements = self.elements[self.index]
        self.index += 1
        return elements 

class OSMHandler:

    # two kind of approaches here, first is custom async iterator, seconc is wrapper func 
    @staticmethod
    async def convert_save_raw_osm_to_model(raw_data: List):
        result = []
        async for elem in AsyncOSMDataIterator(raw_data):
            result.append(OSMtoDBModel(
                id=elem["id"], 
                kante= LineString([[arr_el["lon"], arr_el["lat"]] for arr_el in elem["geometry"]])
            ))
        await insert_osm_json_linestring_into_kanten(result)

    @staticmethod
    async def find_coordinate_boundaries(data: Dict) -> List[float]:
        """Find the min/max latitude and longitude"""
        def calculate_boundaries():
            """Thread-wrapped func"""
            min_x, max_x = 181, -181  # Longitude east and west
            max_y, min_y = -91, 91  # Latitude north and south

            for record in data["features"]:
                record_x, record_y = record["geometry"]["coordinates"]
                min_x = min(min_x, record_x)
                max_x = max(max_x, record_x)
                min_y = min(min_y, record_y)
                max_y = max(max_y, record_y)

            return [round(num, ACCURACY) for num in (min_x, max_x, min_y, max_y)]

        return await asyncio.to_thread(calculate_boundaries)

    @staticmethod 
    async def process_data(data: Dict, filename: str) -> None:
        boundaries = await OSMHandler.find_coordinate_boundaries(data)
        formatted_body = Links.Body.format(
            min_y=boundaries[2], min_x=boundaries[0], max_y=boundaries[3], max_x=boundaries[1]
        )
        Links.Encoded = Links.BaseURL + urllib.parse.quote(formatted_body)

        logging.info(f"Fetching OSM data from: {Links.Encoded} ...")
        try:
            # 300 sec = 5 min timeout
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5*60)) as session:
                async with session.get(Links.Encoded) as resp:
                    if resp.status == 200:
                        osm_data = await resp.json()
                        osm_elements = osm_data["elements"]
                        await OSMHandler.convert_save_raw_osm_to_model(osm_elements)
                    else:
                        logging.error(f"Failed to fetch OSM data. Status code: {resp.status}")
        except aiohttp.ClientError as e:
            logging.error(f"OSM API request failed: {e}")
