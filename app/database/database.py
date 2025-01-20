from sqlalchemy import create_engine, Column, String, Integer, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from datetime import datetime
from app.utils.logger import logger

Base = declarative_base()

class IPAddress(Base):
    __tablename__ = "ip_addresses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ipv4 = Column(String, nullable=False, index=True)
    ipv6 = Column(String, nullable=True)
    
    # Index on ipv6 if you will frequently query by it
    __table_args__ = (Index('ix_ip_addresses_ipv6', 'ipv6'),)

class FailedService(Base):
    __tablename__ = "failed_services"
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_name = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=func.now())

# Database configuration
DATABASE_URL = "sqlite:///./data/wan-ip-provider.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing the database: {e}")
