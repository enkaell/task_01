import asyncio
import asyncpg
import json
from config import DB_URL
from shapely.geometry import LineString
from models import OSMtoDBModel
from typing import List
import logging

async def insert_geojson_linestring_into_befahrungen(line_string: LineString) -> None:
    conn = await asyncpg.connect(DB_URL)
    try:
        await conn.execute("""
            INSERT INTO befahrungen (name, gps_points) VALUES ($1, $2);
        """, "LineString", line_string.wkt)
    except Exception as e:
        logging.error(f"Insert exception as {e}")
    finally:
        logging.info(f"Inserted data succesfully")
        await conn.close()

async def insert_osm_json_linestring_into_kanten(osm_models_list: List[OSMtoDBModel]) -> None:
    conn = await asyncpg.connect(DB_URL)
    values = [(model.id, model.name, model.kante.wkt) for model in osm_models_list]
    try:
        await conn.executemany(
            """
            INSERT INTO kanten (id, name, kante) VALUES ($1, $2, $3);
            """,
            values
        )
    except Exception as e:
        logging.error(f"Insert exception as {e}")
    finally:
        logging.info(f"Inserted data succesfully")
        await conn.close()

async def execute_mapping_of_tables() -> None:
    conn = await asyncpg.connect(DB_URL)
    try:
        # INSERT INTO mapping (kante_id, befahrung_id, gpsindexarray)
        # SELECT 
        #     k.id,  
        #     b.id,  
        #     ARRAY_AGG(i ORDER BY i)  -- Collects and sorts the matched indexes
        # FROM befahrungen b
        # JOIN kanten k 
        # ON ST_DWithin(b.gps_points, k.kante, 1)  -- 1 meter proximity
        # LEFT JOIN LATERAL (
        #     SELECT i
        #     FROM generate_series(1, ST_NumPoints(b.gps_points)) AS i
        #     WHERE ST_DWithin(ST_PointN(b.gps_points, i), k.kante, 1)  
        # ) AS matched_indexes ON true
        # GROUP BY k.id, b.id;

        await conn.execute(
            """
            INSERT INTO kanten (id, name, kante) VALUES ($1, $2, $3);
            """,
            values
        )
    except Exception as e:
        logging.error(f"Insert exception as {e}")
    finally:
        logging.info(f"Inserted data succesfully")
        await conn.close()


async def get_befahrungsabschnitte_as_geojson(befahrung_id: int) -> str:
    conn = await asyncpg.connect(DB_URL)
    try:
        data = await conn.fetchval(
            """
            SELECT ST_AsGeoJSON(gps_points) AS geojson FROM befahrungen WHERE befahrungen.id = $1;
            """, befahrung_id
        )
    except Exception as e:
        logging.error(f"Execution exception as {e}")
    finally:
        logging.info(f"Executed data succesfully")
        await conn.close()
        return json.loads(data)

async def get_all_befahrungen_id() -> List[int]:
    conn = await asyncpg.connect(DB_URL)
    try:
        data = await conn.fetch(
            """
           SELECT id FROM befahrungen;
            """
        )
    except Exception as e:
        logging.error(f"Execution exception as {e}")
    finally:
        logging.info(f"Executed data succesfully")
        await conn.close()
        return [i.get("id") for i in data]