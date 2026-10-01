import os

class Settings:
    PROJECT_NAME: str = "Vehicure - Predictive Vehicle Health & Maintenance Intelligence Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database URIs
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./vehicure.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_TELEMETRY: str = os.getenv("KAFKA_TOPIC_TELEMETRY", "vehicle.telemetry")
    
    # Simulator Config
    SIMULATOR_NUM_VEHICLES: int = int(os.getenv("SIMULATOR_NUM_VEHICLES", "100000"))
    SIMULATOR_DEFAULT_TPS: int = int(os.getenv("SIMULATOR_DEFAULT_TPS", "50"))
    
    # Thresholds for Anomaly Rules
    ENGINE_TEMP_CRITICAL: float = 110.0  # °C
    ENGINE_TEMP_WARNING: float = 98.0   # °C
    BATTERY_VOLTAGE_LOW: float = 11.5   # Volts
    BATTERY_VOLTAGE_HIGH: float = 15.0  # Volts
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "*"]

settings = Settings()
