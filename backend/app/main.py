import asyncio
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.config import settings
from app.database.init_db import init_db
from app.services.simulator import simulator_singleton
from app.services.ml_engine import ml_engine_singleton
from app.services.metrics_tracker import metrics_tracker_singleton

# Import API Routers
from app.api.fleet import router as fleet_router
from app.api.monitoring import router as monitoring_router
from app.api.health import router as health_router
from app.api.alerts import router as alerts_router
from app.api.analytics import router as analytics_router
from app.api.vehicle import router as vehicle_router
from app.api.maintenance import router as maintenance_router
from app.api.system import router as system_router
from app.api.simulator_api import router as simulator_router

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("vehicure.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Initializing Vehicure Connected Vehicle Intelligence backend...")
    
    # 1. Initialize DB tables & seed initial 100K vehicles
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Error during DB initialization: {e}")
        
    # 2. Pre-train Predictive ML Model
    logger.info("Pre-training Predictive Maintenance ML Model (Random Forest vs Baseline)...")
    ml_engine_singleton.train_and_evaluate()
    logger.info(f"ML Model Trained! Precision: {ml_engine_singleton.measured_metrics['primary_model']['precision']}, F1: {ml_engine_singleton.measured_metrics['primary_model']['f1_score']}")

    # 3. Start Telemetry Simulator background task
    asyncio.create_task(simulator_singleton.start_streaming())
    logger.info("Simulator background streaming task started.")
    
    yield
    
    # Shutdown logic
    logger.info("Shutting down Vehicure backend...")
    simulator_singleton.stop_streaming()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Predictive Vehicle Health & Maintenance Intelligence Platform API for 100,000+ Connected Vehicles",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Latency Measurement Middleware
@app.middleware("http")
async def measure_request_latency(request: Request, call_next):
    t0 = time.time()
    response = await call_next(request)
    latency_ms = (time.time() - t0) * 1000.0
    metrics_tracker_singleton.record_api_latency(latency_ms, request.url.path)
    return response

# Mount Prometheus ASGI app at /metrics
prometheus_app = make_asgi_app()
app.mount("/metrics", prometheus_app)

# Include API Routers under /api
app.include_router(fleet_router, prefix=settings.API_PREFIX)
app.include_router(monitoring_router, prefix=settings.API_PREFIX)
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(alerts_router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)
app.include_router(vehicle_router, prefix=settings.API_PREFIX)
app.include_router(maintenance_router, prefix=settings.API_PREFIX)
app.include_router(system_router, prefix=settings.API_PREFIX)
app.include_router(simulator_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {
        "product": "Vehicure",
        "description": "Predictive Vehicle Health & Maintenance Intelligence Platform",
        "status": "ONLINE",
        "docs_url": "/docs",
        "simulated_vehicles": settings.SIMULATOR_NUM_VEHICLES
    }
