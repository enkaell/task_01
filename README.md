# Test task 
## Overview:
Main goal of the project is to normalize given **.geojson** formatted GPS data, based on map data from OSM, meaning the edges of the roads (graph links)

## Project structure

    ├── data                    # Given and sorted data in .geojson
    │    └──Befahrung1.geojson 
    ├── handlers                
    │   ├── geojson_handler.py  # Sorting, validating and save input data in "befahrungen" table
    │   ├── osm_handler.py      # Fetching, validating and save input data in "kanten" table
    │   └──mapping_handler.py   # Mapping the inspection data to the road network
    ├── tests                   # FastAPI tests (pytest)
    ├── config.py
    ├── dabase.py               # Async database workaround via **asyncpg** 
    ├── docker-compose.yaml     # Compose for db(in-build postgis) + app
    ├── Dockerfile              # Multi-stage build for FastAPI application
    ├── main.py                 # FastAPI entrypoint with endpoints
    ├── models.py               # Main communication pydantic models
    ├── req.txt                 # Requirements.txt
    ├── setup_db.py             # Database initialization script based on **psycopg2**
    └── config.py

## Project architecture
![alt text](image.png)

1. User upload .geojson file
2. Two different handlers/workers are processing this file, third awaits for commit in DB
3. When data in Database actualized, third handler finishes job and assigns the edges in the mapping table
4. User can get normalized data in **.geojson** file format as **LineString**  


## 📌  Prerequisites:
- Python 3.9+: Ensure Python is installed on your system
- PostgreSQL with PostGIS: Install PostgreSQL and enable the PostGIS extension for spatial data support
- Docker: For containerized deployment (easiest option)

## 🚀 Raw installation
### 1.Clone repository
```
git clone https://github.com/enkaell/task_01.git
cd task_01
```
### 2. Install Python Dependencies
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3. Configure .env and database.py
```
DATABASE_URL=postgresql://user:password@localhost:5432/mydatabase
```
### 4. Run db initialization script
```
python setup_db.py
```
### 5. Tests with pytest
```
pytest
```
### 6. Run via ASGI
```
uvicorn main:app --host 0.0.0.0 --port 8000
```
## 📡 API Endpoints

## 🔹 1. Import Survey Data

 > **Endpoint**: POST /befahrungsabschnitte/

**Description**: Accepts a GeoJSON file, sort it and creates new file in **/data** in **filename_sorted.geojson** format, then after imports it into the database, processes relevant OSM data, and maps GPS data to road segments

**Usage**:
```
curl -X POST "http://localhost:8000/befahrungsabschnitte/" -F "file=@path_to_your_file.geojson"
```
## 🔹 2. Retrieve Survey Segments

**Endpoint**: GET /befahrungsabschnitte/

**Description**: Returns all survey segments as **GeoJSON** LineString objects. GeoJSON format can be pasted in OSM map,resulted example:

 ![alt text](image-1.png)

**Usage:**
```
curl -X GET "http://localhost:8000/befahrungsabschnitte/"
```
## 🐳 Docker-compose Deployment

To deploy the application using Docker:

## 1️⃣ Build the Docker Image

docker build -t fastapi-app . 

## 2️⃣ Build and run the Docker-compose

docker-compose up --build  

Ensure your PostgreSQL database is accessible to the container, either by configuring network settings or using Docker Compose. Tests are done automatically after build stage.

## 🎯 Done:
### ✅ Working processing data pipeline
### ✅ Solution based on asyncio
### ✅ GIST Index is used for better SQL-queries execution time + [ST_Dwithin](https://postgis.net/workshops/postgis-intro/spatial_relationships.html)
### ✅ Followed ACID transaction principles
### ✅ Test-covered with PyTest
### ✅ Packaged in Docker + Docker compose

## ✍️ TODO:
### ❌ Better approach for gathering data from OSM:
By default I am using **bbox**, maybe **poly** with dots connection algorithm would be a nice idea OR local deployment of [OSM database](https://wiki.openstreetmap.org/wiki/Setting_up_a_local_copy_of_the_OpenStreetMap_database,_kept_up_to_date_with_minutely_diffs) without request timeouts
### ❌ Cprofiling and performance evaluation
### ❌ Integration tests + mocking tests (?)
### ❌ Multi-language support in .env



