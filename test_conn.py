from pymongo import MongoClient
import config

try:
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()  # fuerza conexión
    print("Conectado a MongoDB Atlas correctamente")
except Exception as e:
    print("Error de conexión:", e)
