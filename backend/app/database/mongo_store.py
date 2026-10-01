import logging
from typing import Dict, Any, List

logger = logging.getLogger("vehicure.mongo")

class MongoStore:
    """
    MongoDB adapter for raw high-volume telemetry event storage.
    Supports in-memory ring buffer fallback if MongoDB is not running locally.
    """
    def __init__(self, mongo_url: str):
        self.mongo_url = mongo_url
        self.client = None
        self.db = None
        self.telemetry_coll = None
        self.in_memory_events: List[Dict[str, Any]] = []
        self.max_in_memory_capacity = 10000

    async def connect(self):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.mongo_url, serverSelectionTimeoutMS=2000)
            self.client.admin.command('ping')
            self.db = self.client["vehicure_telemetry"]
            self.telemetry_coll = self.db["raw_events"]
            logger.info("Connected to MongoDB for raw telemetry storage.")
        except Exception as e:
            logger.warning(f"MongoDB connection failed ({e}). Using in-memory ring buffer for raw telemetry.")
            self.client = None
            self.telemetry_coll = None

    async def insert_event(self, event: Dict[str, Any]):
        if self.telemetry_coll is not None:
            try:
                self.telemetry_coll.insert_one(event)
                return
            except Exception:
                pass
        
        # Fallback to ring buffer
        if len(self.in_memory_events) >= self.max_in_memory_capacity:
            self.in_memory_events.pop(0)
        self.in_memory_events.append(event)

    async def get_recent_events_for_vehicle(self, vin: str, limit: int = 50) -> List[Dict[str, Any]]:
        if self.telemetry_coll is not None:
            try:
                cursor = self.telemetry_coll.find({"vin": vin}).sort("timestamp", -1).limit(limit)
                events = list(cursor)
                for e in events:
                    if "_id" in e:
                        e["_id"] = str(e["_id"])
                return events
            except Exception:
                pass
        
        # Filter from in-memory ring buffer
        matching = [e for e in reversed(self.in_memory_events) if e.get("vin") == vin]
        return matching[:limit]
