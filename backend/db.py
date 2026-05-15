import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from flask import jsonify, Blueprint

# blueprint
db_bp = Blueprint("database", __name__)

@db_bp.route('/api/message', methods=["GET"])
def home():
    return jsonify({"message": "running..."})

# load env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# engine
engine = create_engine(DATABASE_URL, echo=True)
conn = engine.connect()

# session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for models
Base = declarative_base()

print("Connected to DB")
