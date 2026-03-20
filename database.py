# database.py
# This file creates the connection between FastAPI and your Supabase PostgreSQL database

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load values from your .env file
load_dotenv()

# Get the database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the database engine
# This is the actual connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory that creates database sessions
# Each API request gets its own session, then closes it when done
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class all your models (tables) will inherit from
Base = declarative_base()

# This function is used in every API endpoint as a dependency
# It opens a DB session, gives it to the endpoint, then closes it automatically
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()