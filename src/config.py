import os
import logging
import sys
from dotenv import load_dotenv

load_dotenv() 
sys.dont_write_bytecode = True
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

ACCURACY = int(os.getenv("ACCURACY", 6))
DB_NAME = os.getenv("DB_NAME", "task1")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"