from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Fleet(Base):
    __tablename__ = "fleets"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicles = relationship("Vehicle", back_populates="fleet")

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    vin = Column(String(17), primary_key=True)
    fleet_id = Column(String(50), ForeignKey("fleets.id"), nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    fuel_type = Column(String(20), default="GASOLINE")  # GASOLINE, DIESEL, ELECTRIC, HYBRID
    odometer_km = Column(Float, default=0.0)
    status = Column(String(20), default="ACTIVE")       # ACTIVE, IDLE, IN_SERVICE, CRITICAL
    
    health_score = Column(Float, default=100.0)
    risk_score = Column(Float, default=0.0)             # 0 to 100
    risk_level = Column(String(20), default="LOW")      # LOW, MEDIUM, HIGH, CRITICAL
    failure_prob = Column(Float, default=0.0)           # Percentage 0.0 to 100.0
    
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    last_speed_kmh = Column(Float, default=0.0)
    last_engine_temp = Column(Float, default=90.0)
    last_battery_voltage = Column(Float, default=12.6)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    fleet = relationship("Fleet", back_populates="vehicles")
    alerts = relationship("Alert", back_populates="vehicle")
    maintenance_orders = relationship("MaintenanceOrder", back_populates="vehicle")

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(String(50), primary_key=True)
    vin = Column(String(17), ForeignKey("vehicles.vin"), nullable=True)
    name = Column(String(100), nullable=False)
    license_num = Column(String(50), nullable=False)
    safety_score = Column(Float, default=95.0)

class DtcCatalog(Base):
    __tablename__ = "dtc_catalog"
    
    code = Column(String(10), primary_key=True)
    description = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)       # CRITICAL, HIGH, MEDIUM, LOW
    category = Column(String(50), nullable=False)       # ENGINE, BATTERY, TRANSMISSION, BRAKES
    recommended_action = Column(Text, nullable=False)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String(50), primary_key=True)
    vin = Column(String(17), ForeignKey("vehicles.vin"), nullable=False)
    severity = Column(String(20), nullable=False)       # CRITICAL, HIGH, MEDIUM, LOW
    reason = Column(Text, nullable=False)
    dtc_code = Column(String(10), nullable=True)
    recommended_action = Column(Text, nullable=False)
    status = Column(String(20), default="ACTIVE")       # ACTIVE, ACKNOWLEDGED, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    vehicle = relationship("Vehicle", back_populates="alerts")

class MaintenanceOrder(Base):
    __tablename__ = "maintenance_orders"
    
    id = Column(String(50), primary_key=True)
    vin = Column(String(17), ForeignKey("vehicles.vin"), nullable=False)
    priority = Column(String(20), default="HIGH")       # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="SCHEDULED")    # SCHEDULED, IN_PROGRESS, COMPLETED
    scheduled_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="maintenance_orders")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(50), primary_key=True)
    user_name = Column(String(100), default="System")
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
