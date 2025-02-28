import json
import os
import logging
import asyncio
from fastapi import Depends, FastAPI, UploadFile, status, HTTPException
from handlers.geojson_handler import GeoJSONHandler
from handlers.mapping_handler import mapping_handler
from handlers.osm_handler import OSMHandler
from database import get_befahrungsabschnitte_as_geojson, get_all_befahrungen_id
from models import BefahrungRequest

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile):
    if file.filename[-8:len(file.filename)] != ".geojson":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong file format")
    if file.filename.replace(".geojson", "_sorted.geojson") in os.listdir("data"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File was already uploaded")
    try:
        data = json.load(file.file)
    except json.JSONDecodeError as e:
        logging.error(f"Error opening file: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON file")

    # Laufen in der Hintergrund
    async def process_and_map():
        """Big Handlers are running in parallel, mapping wait for them"""
        await asyncio.gather(
            GeoJSONHandler.process_data(data, file.filename),
            OSMHandler.process_data(data, file.filename)
        )
        await mapping_handler()

    # Start the parallel tasks
    asyncio.create_task(process_and_map())
    # return result of the validation to user!!
    return {"detail": "File uploaded"}


# KEINE SERVICE ISOLATION HIER, METHODEN ZIEHEN DIREKT VOM DATENBANK FILE
@app.get("/befahrungsabschnitte/alle")
async def get_alle_befahrungsabschnitte_ids():
    res = await get_all_befahrungen_id()
    return {"list": res}

# KEINE SERVICE ISOLATION HIER, METHODEN ZIEHEN DIREKT VOM DATENBANK FILE
# Sensitiv Daten in Request Body
@app.post("/befahrungsabschnitte")
async def get_befahrungsabschnitte_by_id(request: BefahrungRequest):
    id_list = await get_all_befahrungen_id()
    if request.befahrung_id not in id_list:
        raise HTTPException(status_code=404, detail="This file wasn't processed")
    data = await get_befahrungsabschnitte_as_geojson(request.befahrung_id)
    return data