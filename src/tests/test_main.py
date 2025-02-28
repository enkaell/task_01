from fastapi.testclient import TestClient
# TODO: Fix this import....
from main import app
from models import BefahrungRequest
import os
client = TestClient(app)

def test_get_alle_befahrungsabschnitte_empty():
    response = client.get("/befahrungsabschnitte/alle")
    assert response.status_code == 200
    assert response.json() == {'list': []}


def test_upload_not_geojson_file():
    response = client.post("/upload", files= {'file': (open(os.path.join("tests", "test1.json"), "rb"))})
    assert response.status_code == 400
    assert response.json()["detail"] == "Wrong file format"

def test_upload_valid_file():
    response = client.post("/upload", files= {'file': (open(os.path.join("tests", "test1.geojson"), "rb"))})
    assert response.status_code == 200
    assert response.json()["detail"] == "File uploaded"

def test_upload_invalid_openjson():
    response = client.post("/upload", files= {'file': (open(os.path.join("tests", "test1_invalid.geojson"), "rb"))})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid JSON file"

def test_get_alle_befahrungsabschnitte():
    response = client.get("/befahrungsabschnitte/alle")
    assert response.status_code == 200
    assert response.json() == {'list': [1]}

def test_get_befahrungsabschnitte_by_id_invalid():
    response = client.post("/befahrungsabschnitte", json={"befahrung_id":998})
    assert response.status_code == 404
    assert response.json()["detail"] == "This file wasn't processed"

def test_get_befahrungsabschnitte_by_id_valid():
    response = client.post("/befahrungsabschnitte", json={"befahrung_id":1})
    assert response.status_code == 200
    assert type(response.json()) == dict



# :TODO tests
# Mock /data dir?
# def test_upload_valid_once_more():
#     response = client.post("/upload", files= {'file': (open(os.path.join("tests", "test1_sorted.geojson"), "rb"))})
#     assert response.status_code == 400
#     assert response.json()["detail"] == "File was already uploaded"
