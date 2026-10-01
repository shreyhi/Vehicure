import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("vehicure.redis")

class RedisStore:
    """
    Redis adapter for caching recent vehicle states, Bloom filter backup, and real-time metrics.
    Fallback to in-memory dictionary if Redis is unavailable.
    """
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client = None
        self.in_memory_cache: Dict[str, str] = {}
        self.in_memory_sets: Dict[str, set] = {}

    async def connect(self):
        try:
            import redis.asyncio as aioredis
            self.client = aioredis.from_url(self.redis_url, decode_responses=True)
            await self.client.ping()
            logger.info("Connected to Redis server successfully.")
        except Exception as e:
            logger.warning(f"Redis connection failed ({e}). Falling back to high-speed in-memory store.")
            self.client = None

    async def set_vehicle_state(self, vin: str, state: Dict[str, Any], ttl_seconds: int = 86400):
        data = json.dumps(state)
        if self.client:
            try:
                await self.client.set(f"vehicle:{vin}:state", data, ex=ttl_seconds)
            except Exception:
                self.in_memory_cache[f"vehicle:{vin}:state"] = data
        else:
            self.in_memory_cache[f"vehicle:{vin}:state"] = data

    async def get_vehicle_state(self, vin: str) -> Optional[Dict[str, Any]]:
        data = None
        if self.client:
            try:
                data = await self.client.get(f"vehicle:{vin}:state")
            except Exception:
                data = self.in_memory_cache.get(f"vehicle:{vin}:state")
        else:
            data = self.in_memory_cache.get(f"vehicle:{vin}:state")
            
        if data:
            return json.loads(data)
        return None

    async def add_seq_idempotency(self, vin: str, seq: int) -> bool:
        """
        Returns True if seq is NEW (added successfully), False if DUPLICATE.
        """
        key = f"vehicle:{vin}:seqs"
        if self.client:
            try:
                added = await self.client.sadd(key, str(seq))
                return added == 1
            except Exception:
                pass
        
        if key not in self.in_memory_sets:
            self.in_memory_sets[key] = set()
        if str(seq) in self.in_memory_sets[key]:
            return False
        self.in_memory_sets[key].add(str(seq))
        return True
