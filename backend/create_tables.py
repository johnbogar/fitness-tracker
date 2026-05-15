"""
create_tables.py
----------------
Creates all database tables needed by the fitness tracker app.

Run from the /backend directory:
    python create_tables.py

Tables created:
  "Users"    -- raw SQL (no SQLAlchemy model exists for this table)
  "Goals"    -- via SQLAlchemy ORM model  (models/goal.py)
  "Workouts" -- via SQLAlchemy ORM model  (models/workout.py)
"""

from sqlalchemy import text

# 1. Import the shared engine + Base from db.py
from db import engine, Base

# 2. Import ORM models so they register themselves on Base.metadata
#    This MUST happen before Base.metadata.create_all(), otherwise
#    SQLAlchemy doesn't know about those tables.
from models.goal import Goal        # registers "Goals"
from models.workout import Workout  # registers "Workouts"

# 3. Raw SQL for "Users" — auth.py uses this table but no ORM model exists
CREATE_USERS = text("""
CREATE TABLE IF NOT EXISTS "Users" (
    id            SERIAL      PRIMARY KEY,
    firstname     TEXT        NOT NULL,
    lastname      TEXT        NOT NULL,
    email         TEXT        NOT NULL UNIQUE,
    password      TEXT        NOT NULL,
    creationdate  TIMESTAMP   NOT NULL DEFAULT NOW()
);
""")

print("Creating database tables...")
print("=" * 50)

try:
    # Create Users via raw SQL
    with engine.begin() as conn:
        conn.execute(CREATE_USERS)
    print("  [OK] Users")

    # Create Goals + Workouts via ORM (IF NOT EXISTS is implicit with checkfirst=True)
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("  [OK] Goals")
    print("  [OK] Workouts")

    # Add estimated_workouts column to Goals (safe to run even if already exists)
    with engine.begin() as conn:
        conn.execute(text(
            'ALTER TABLE "Goals" ADD COLUMN IF NOT EXISTS estimated_workouts INTEGER DEFAULT 10;'
        ))
    print("  [OK] Goals.estimated_workouts column")

    print("=" * 50)
    print("SUCCESS: All tables and migrations are ready.")
    print("You can now register an account and log in.")

except Exception as e:
    print(f"ERROR: {e}")
    print("\nTroubleshooting:")
    print("  1. Check DATABASE_URL in backend/.env")
    print("  2. Confirm the Railway database service is running")
    print("  3. If using SSL, make sure the URL includes ?sslmode=require")