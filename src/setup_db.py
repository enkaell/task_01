import psycopg2
import logging
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

logging.basicConfig(level=logging.INFO)

# :TODO data insertion pipeline is not stabil und straight-forward

# Connect to 'postgres' to create database
connection = psycopg2.connect(
    dbname="postgres",
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
connection.autocommit = True
cursor = connection.cursor()

# Check if the database exists
cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
exists = cursor.fetchone()

if not exists:
    cursor.execute(f"CREATE DATABASE {DB_NAME};")
    logging.info(f"Database '{DB_NAME}' created successfully")
else:
    logging.warning(f"Database '{DB_NAME}' already exists")

cursor.close()
connection.close()


# Establish new connection to created database
connection = psycopg2.connect(
    dbname=DB_NAME,  
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
connection.autocommit = True
cursor = connection.cursor()

# PostGIS
cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
logging.info("PostGIS extension enabled")

# Create tables
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS befahrungen (
            id serial primary key,
            name TEXT NOT NULL,
            gps_points geometry NOT NULL
        );
    """)
    logging.info("Table 'befahrungen' created")
except Exception as e:
    logging.error(f"Error creating 'befahrungen': {e}")

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kanten (
            id BIGINT PRIMARY KEY,
            name TEXT NOT NULL,
            kante geometry not null
        );
    """)
    logging.info("Table 'kanten' created")
except Exception as e:
    logging.error(f"Error creating 'kanten': {e}")

try:
    cursor.execute("""
        CREATE TABLE mapping (
            id SERIAL PRIMARY KEY,
            kante_id BIGINT REFERENCES kanten(id) ON DELETE CASCADE,
            befahrung_id BIGINT REFERENCES befahrungen(id) ON DELETE CASCADE,
            GPSIndexArray BIGINT[] not null
        );
    """)
    logging.info("Table 'mapping' created")
except Exception as e:
    logging.error(f"Error creating 'kanten': {e}")

try:
    cursor.execute("""
        CREATE INDEX ON befahrungen USING GIST (gps_points);
        CREATE INDEX ON kanten USING GIST (kante);
    """)
    logging.info("Indexes created")
except Exception as e:
    logging.error(f"Error creating indexes: {e}")
    
connection.commit()
cursor.close()
connection.close()
