import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    username = Column(String, nullable=False, default="User")
    tortilla_qty = Column(Float, nullable=False, default=0.0)
    totopos_qty = Column(Float, nullable=False, default=0.0)
    cacahuates_qty = Column(Float, nullable=False, default=0.0)
    mix_qty = Column(Float, nullable=False, default=0.0)
    salted_chips_qty = Column(Float, nullable=False, default=0.0)
    special_qty = Column(Float, nullable=False, default=0.0)
    special_price = Column(Float, nullable=False, default=0.0)
    frequent_customer = Column(Boolean, nullable=False, default=False)
    supplier = Column(Boolean, nullable=False, default=False)
    total = Column(Float, nullable=False)
    payment = Column(Float, nullable=False)
    change = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False