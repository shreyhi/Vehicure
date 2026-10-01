import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.db_models import Base, Fleet, Vehicle, Driver, DtcCatalog, Alert, MaintenanceOrder, AuditLog
from app.utils.vin_generator import generate_vin

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

DTC_CATALOG_SEED = [
    {"code": "P0300", "description": "Random/Multiple Cylinder Misfire Detected", "severity": "CRITICAL", "category": "ENGINE", "action": "Inspect spark plugs, ignition coils, and fuel injectors immediately."},
    {"code": "P0301", "description": "Cylinder 1 Misfire Detected", "severity": "HIGH", "category": "ENGINE", "action": "Check ignition coil and spark plug on Cylinder 1."},
    {"code": "P0217", "description": "Engine Coolant Overtemperature Condition", "severity": "CRITICAL", "category": "ENGINE", "action": "Stop vehicle safely. Inspect coolant level, radiator fan, and thermostat."},
    {"code": "P0117", "description": "Engine Coolant Temp Sensor Circuit Low Input", "severity": "MEDIUM", "category": "ENGINE", "action": "Check engine coolant temperature sensor wiring and connector."},
    {"code": "P0420", "description": "Catalytic Converter System Efficiency Below Threshold", "severity": "MEDIUM", "category": "EXHAUST", "action": "Inspect catalytic converter and O2 sensors for degradation."},
    {"code": "P0562", "description": "System Voltage Low", "severity": "HIGH", "category": "BATTERY", "action": "Test battery charge, alternator output, and battery terminal connections."},
    {"code": "P0563", "description": "System Voltage High", "severity": "HIGH", "category": "BATTERY", "action": "Check voltage regulator and alternator charging system."},
    {"code": "P0700", "description": "Transmission Control System Malfunction", "severity": "CRITICAL", "category": "TRANSMISSION", "action": "Schedule transmission diagnostic scan and inspect fluid levels."}
]

FLEETS_SEED = [
    {"id": "FLT-001", "name": "Volvo North America Fleet", "region": "US-East"},
    {"id": "FLT-002", "name": "Subaru Cross-Country Logistics", "region": "US-West"},
    {"id": "FLT-003", "name": "Stellantis Commercial Transports", "region": "US-Central"},
    {"id": "FLT-004", "name": "Ford Metro Delivery Services", "region": "US-South"},
    {"id": "FLT-005", "name": "Tesla EV Express Fleet", "region": "US-Northeast"}
]

OEM_MAKES = {
    "FLT-001": ("Volvo", ["XC90", "V60", "FH16", "EX90"]),
    "FLT-002": ("Subaru", ["Outback", "Forester", "Solterra"]),
    "FLT-003": ("Stellantis", ["Ram 1500", "ProMaster", "Jeep Cherokee"]),
    "FLT-004": ("Ford", ["F-150 Lightning", "E-Transit", "Explorer"]),
    "FLT-005": ("Tesla", ["Model Y Fleet", "Semi", "Model 3 Long Range"])
}

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        # Check if already initialized
        result = await session.execute(Base.metadata.tables["fleets"].select())
        if result.first():
            print("Database already initialized with fleets and vehicles.")
            return

        print("Seeding database with fleets, DTC catalog, and 100,000 simulated vehicles...")
        
        # Seed Fleets
        for f in FLEETS_SEED:
            session.add(Fleet(id=f["id"], name=f["name"], region=f["region"]))
            
        # Seed DTC Catalog
        for dtc in DTC_CATALOG_SEED:
            session.add(DtcCatalog(
                code=dtc["code"],
                description=dtc["description"],
                severity=dtc["severity"],
                category=dtc["category"],
                recommended_action=dtc["action"]
            ))
        
        await session.commit()
        
        # Batch insert 100,000 synthetic vehicles
        # To maintain quick startup while supporting 100K vehicle querying, we seed vehicles in chunks
        batch_size = 5000
        total_vehicles = settings.SIMULATOR_NUM_VEHICLES  # 100,000
        
        for batch_idx in range(0, total_vehicles, batch_size):
            vehicles_batch = []
            for i in range(batch_idx, min(batch_idx + batch_size, total_vehicles)):
                fleet_id = f"FLT-00{(i % 5) + 1}"
                make, models = OEM_MAKES[fleet_id]
                model = random.choice(models)
                year = random.randint(2020, 2026)
                fuel_type = "ELECTRIC" if "EX90" in model or "Lightning" in model or "Tesla" in make or "Solterra" in model else "GASOLINE"
                vin = generate_vin(make)
                
                # Distribution: 85% Healthy, 10% Medium Risk, 4% High Risk, 1% Critical
                rnd = random.random()
                if rnd < 0.85:
                    health = round(random.uniform(85, 100), 1)
                    risk_score = round(100 - health, 1)
                    risk_level = "LOW"
                    fail_prob = round(random.uniform(1.0, 8.0), 1)
                    temp = round(random.uniform(85, 95), 1)
                    batt = round(random.uniform(12.4, 13.2), 1)
                elif rnd < 0.95:
                    health = round(random.uniform(60, 84), 1)
                    risk_score = round(100 - health, 1)
                    risk_level = "MEDIUM"
                    fail_prob = round(random.uniform(15.0, 35.0), 1)
                    temp = round(random.uniform(96, 102), 1)
                    batt = round(random.uniform(11.8, 12.2), 1)
                elif rnd < 0.99:
                    health = round(random.uniform(35, 59), 1)
                    risk_score = round(100 - health, 1)
                    risk_level = "HIGH"
                    fail_prob = round(random.uniform(45.0, 75.0), 1)
                    temp = round(random.uniform(103, 112), 1)
                    batt = round(random.uniform(11.2, 11.7), 1)
                else:
                    health = round(random.uniform(10, 34), 1)
                    risk_score = round(100 - health, 1)
                    risk_level = "CRITICAL"
                    fail_prob = round(random.uniform(80.0, 98.0), 1)
                    temp = round(random.uniform(113, 125), 1)
                    batt = round(random.uniform(10.5, 11.2), 1)
                    
                v = Vehicle(
                    vin=vin,
                    fleet_id=fleet_id,
                    make=make,
                    model=model,
                    year=year,
                    fuel_type=fuel_type,
                    odometer_km=round(random.uniform(5000, 180000), 1),
                    status="CRITICAL" if risk_level == "CRITICAL" else ("ACTIVE" if random.random() > 0.2 else "IDLE"),
                    health_score=health,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    failure_prob=fail_prob,
                    last_latitude=round(37.7749 + random.uniform(-5.0, 5.0), 4),
                    last_longitude=round(-122.4194 + random.uniform(-5.0, 5.0), 4),
                    last_speed_kmh=round(random.uniform(0, 110), 1),
                    last_engine_temp=temp,
                    last_battery_voltage=batt,
                    last_seen=datetime.utcnow() - timedelta(minutes=random.randint(0, 60))
                )
                vehicles_batch.append(v)
                
                # Seed critical/high risk alerts
                if risk_level in ["CRITICAL", "HIGH"] and i % 50 == 0:
                    dtc = random.choice(DTC_CATALOG_SEED)
                    session.add(Alert(
                        id=f"ALT-{i:06d}",
                        vin=vin,
                        severity=dtc["severity"],
                        reason=f"High Failure Risk ({fail_prob}%) - {dtc['description']}",
                        dtc_code=dtc["code"],
                        recommended_action=dtc["action"],
                        status="ACTIVE",
                        created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                    ))
            
            session.add_all(vehicles_batch)
            await session.commit()
            print(f"Seeded vehicles {batch_idx + len(vehicles_batch)} / {total_vehicles}...")
            
        print("Database initialization complete!")

if __name__ == "__main__":
    asyncio.run(init_db())
