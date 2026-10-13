from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

# Read DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create PostgreSQL Engine
engine = create_engine(DATABASE_URL)

# Create Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===== DB Connection Check =====
from sqlalchemy import text

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        print("Connected to PostgreSQL Successfully!")
except Exception as e:
    print(f"Connection Failed:\n{e}")