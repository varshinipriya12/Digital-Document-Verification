import json
import os
import logging
from datetime import datetime, timezone
from pymongo import MongoClient
import mongomock
from config import Config

logger = logging.getLogger(__name__)

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db.json")

def _serialize_val(val):
    if isinstance(val, datetime):
        return {"__type__": "datetime", "val": val.isoformat()}
    if isinstance(val, dict):
        return {k: _serialize_val(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_serialize_val(v) for v in val]
    if hasattr(val, '__class__') and val.__class__.__name__ == 'ObjectId':
        return str(val)
    return val

def _deserialize_val(val):
    if isinstance(val, dict):
        if val.get("__type__") == "datetime" and "val" in val:
            try:
                return datetime.fromisoformat(val["val"])
            except Exception:
                return val["val"]
        return {k: _deserialize_val(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_deserialize_val(v) for v in val]
    return val

class PersistentCollection:
    def __init__(self, collection, disk_db):
        self._col = collection
        self._disk_db = disk_db

    def __getattr__(self, name):
        attr = getattr(self._col, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                res = attr(*args, **kwargs)
                if name in ("insert_one", "insert_many", "update_one", "update_many", "delete_one", "delete_many", "find_one_and_update", "replace_one"):
                    self._disk_db.save_to_disk()
                return res
            return wrapper
        return attr

    def __getitem__(self, item):
        return self._col[item]

class DiskPersistentDB:
    def __init__(self, raw_db, filepath):
        self._raw_db = raw_db
        self.filepath = filepath
        self.load_from_disk()

    def __getitem__(self, col_name):
        return PersistentCollection(self._raw_db[col_name], self)

    def __getattr__(self, name):
        return getattr(self._raw_db, name)

    def save_to_disk(self):
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            data = {}
            for col_name in self._raw_db.list_collection_names():
                docs = list(self._raw_db[col_name].find({}))
                data[col_name] = [_serialize_val(d) for d in docs]
            
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving database to disk ({self.filepath}): {e}")

    def load_from_disk(self):
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for col_name, docs in data.items():
                col = self._raw_db[col_name]
                col.delete_many({})
                restored = [_deserialize_val(d) for d in docs]
                if restored:
                    col.insert_many(restored)
            logger.info(f"Successfully loaded persistent database from {self.filepath}")
        except Exception as e:
            logger.error(f"Error loading database from disk ({self.filepath}): {e}")

class Database:
    db = None
    client = None
    is_mock = False

    @classmethod
    def get_db(cls):
        if cls.db is not None:
            return cls.db
        
        try:
            # Try connecting to real MongoDB instance with a short timeout
            cls.client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=2000)
            cls.client.admin.command('ping')
            cls.db = cls.client[Config.DB_NAME]
            cls.is_mock = False
            logger.info(f"Successfully connected to MongoDB at {Config.MONGODB_URI}")
        except Exception as e:
            logger.warning(f"Could not connect to live MongoDB: {e}. Falling back to disk-persistent Mongomock database ({DB_FILE}).")
            cls.client = mongomock.MongoClient()
            raw_db = cls.client[Config.DB_NAME]
            cls.db = DiskPersistentDB(raw_db, DB_FILE)
            cls.is_mock = True

        return cls.db

    @classmethod
    def get_collection(cls, collection_name):
        db = cls.get_db()
        return db[collection_name]

# Helper shorthand getters for collections specified in database design
def get_users_collection():
    return Database.get_collection("users")

def get_services_collection():
    return Database.get_collection("government_services")

def get_documents_collection():
    return Database.get_collection("documents")

def get_service_documents_collection():
    return Database.get_collection("service_documents")

def get_uploads_collection():
    return Database.get_collection("uploads")

def get_verification_results_collection():
    return Database.get_collection("verification_results")

def get_verification_sessions_collection():
    return Database.get_collection("verification_sessions")

def get_otps_collection():
    return Database.get_collection("otps")
