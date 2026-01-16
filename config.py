# config.py
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv(
    "MONGO_URI",
    ""
)

MONGO_DB_NAME = os.getenv(
    "MONGO_DB_NAME",
    "ProyectoIntegrador"
)

SECRET_KEY = os.getenv("SECRET_KEY", "cambiar_esto")
