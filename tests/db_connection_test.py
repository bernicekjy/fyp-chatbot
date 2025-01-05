from pymongo import MongoClient
import os

db_connection_str = os.environ.get("AZURE_COSMOSDB_CONNECTION_STR")
client = MongoClient(db_connection_str)
try:
    client.server_info()  # Force connection on a request
    print("Connected to MongoDB!")
except Exception as e:
    print(f"Connection failed: {e}")
