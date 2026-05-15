"""
populate_dummy_data.py
----------------------
Populates the database with realistic test data for development/demo.

Run from the /backend directory:
    python3 populate_dummy_data.py

Creates:
  - 2 test users  (jp@test.com and alex@test.com, password: password123)
  - JP:   3 goals, 15 workouts spread realistically across the last 3 weeks
  - Alex: 2 goals,  5 workouts

Idempotent — safe to run multiple times. Skips data that already exists.
"""

from datetime import date, timedelta, datetime, timezone
from werkzeug.security import generate_password_hash
from sqlalchemy import text

from db import engine, SessionLocal
from models.goal import Goal
from models.workout import Workout

# ── Test users ────────────────────────────────────────────────────────────────
TEST_USERS = [
    {'firstname': 'JP',   'lastname': 'Bogar', 'email': 'jp@test.com',   'password': 'password123'},
    {'firstname': 'Alex', 'lastname': 'Smith', 'email': 'alex@test.com', 'password': 'password123'},
]

# ── JP's goals ────────────────────────────────────────────────────────────────
today = date.today()
now   = datetime.now(timezone.utc)

JP_GOALS = [
    {
        'goalname':           'Run Marathon',
        'goaldesc':           'Train to complete a full 26.2-mile marathon',
        'estimated_workouts': 20,
        'creationdate':       now - timedelta(days=30),
        'enddate':            today + timedelta(days=60),
    },
    {
        'goalname':           'Lose 10 lbs',
        'goaldesc':           'Reach target weight through cardio and clean eating',
        'estimated_workouts': 15,
        'creationdate':       now - timedelta(days=25),
        'enddate':            today + timedelta(days=45),
    },
    {
        'goalname':           'Build Muscle',
        'goaldesc':           'Increase strength and muscle mass with weight training',
        'estimated_workouts': 12,
        'creationdate':       now - timedelta(days=20),
        'enddate':            today + timedelta(days=40),
    },
]

# goal_idx refers to index in JP_GOALS list above
JP_WORKOUTS = [
    # Run Marathon — 8 workouts spread over last 3 weeks
    {'goal_idx': 0, 'days_ago': 21, 'notes': 'First long run — 8 miles. Felt great!'},
    {'goal_idx': 0, 'days_ago': 19, 'notes': 'Easy 5-mile recovery run'},
    {'goal_idx': 0, 'days_ago': 17, 'notes': 'Speed intervals on the track'},
    {'goal_idx': 0, 'days_ago': 14, 'notes': 'Long run — 10 miles. Tough but worth it'},
    {'goal_idx': 0, 'days_ago': 12, 'notes': 'Easy recovery day, legs were sore'},
    {'goal_idx': 0, 'days_ago':  9, 'notes': '6 miles with hill repeats'},
    {'goal_idx': 0, 'days_ago':  5, 'notes': 'Tempo run — felt really strong today'},
    {'goal_idx': 0, 'days_ago':  2, 'notes': '12-mile long run — personal best distance!'},
    # Lose 10 lbs — 5 workouts over last 2 weeks
    {'goal_idx': 1, 'days_ago': 13, 'notes': '45-min cardio session on the elliptical'},
    {'goal_idx': 1, 'days_ago': 11, 'notes': 'HIIT workout — super intense, burned 600 cal'},
    {'goal_idx': 1, 'days_ago':  8, 'notes': 'Stationary cycling — 30 minutes'},
    {'goal_idx': 1, 'days_ago':  6, 'notes': 'Swimming laps — great low-impact cross-training'},
    {'goal_idx': 1, 'days_ago':  3, 'notes': 'Jump rope and core work, 40 minutes'},
    # Build Muscle — 2 workouts from last week
    {'goal_idx': 2, 'days_ago':  7, 'notes': 'Upper body — hit a new bench press PR!'},
    {'goal_idx': 2, 'days_ago':  4, 'notes': 'Leg day — heavy squats and deadlifts'},
]

# ── Alex's goals ──────────────────────────────────────────────────────────────
ALEX_GOALS = [
    {
        'goalname':           'Stay Active',
        'goaldesc':           'Work out at least 3 times per week consistently',
        'estimated_workouts': 10,
        'creationdate':       now - timedelta(days=15),
        'enddate':            today + timedelta(days=30),
    },
    {
        'goalname':           'Improve Flexibility',
        'goaldesc':           'Daily stretching and yoga practice',
        'estimated_workouts': 8,
        'creationdate':       now - timedelta(days=10),
        'enddate':            None,
    },
]

ALEX_WORKOUTS = [
    {'goal_idx': 0, 'days_ago': 14, 'notes': 'Morning run around the park'},
    {'goal_idx': 0, 'days_ago': 11, 'notes': 'Full gym session'},
    {'goal_idx': 0, 'days_ago':  8, 'notes': 'Bike ride — 45 minutes'},
    {'goal_idx': 1, 'days_ago':  9, 'notes': '30-min yoga flow'},
    {'goal_idx': 1, 'days_ago':  5, 'notes': 'Stretching and meditation session'},
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def ensure_column():
    """Make sure estimated_workouts column exists (safe if already present)."""
    with engine.begin() as conn:
        conn.execute(text(
            'ALTER TABLE "Goals" ADD COLUMN IF NOT EXISTS estimated_workouts INTEGER DEFAULT 10;'
        ))


def get_or_create_user(conn, user_data):
    """Return user_id for existing user, or insert and return new id."""
    row = conn.execute(
        text('SELECT id FROM "Users" WHERE email = :email'),
        {'email': user_data['email']}
    ).fetchone()

    if row:
        print(f"  [EXISTS]  {user_data['email']}  (id={row[0]})")
        return row[0]

    hashed = generate_password_hash(user_data['password'])
    new_row = conn.execute(
        text('''
            INSERT INTO "Users" (firstname, lastname, email, password, creationdate)
            VALUES (:fn, :ln, :email, :pw, NOW())
            RETURNING id
        '''),
        {'fn': user_data['firstname'], 'ln': user_data['lastname'],
         'email': user_data['email'],  'pw': hashed}
    ).fetchone()
    print(f"  [CREATED] {user_data['email']}  (id={new_row[0]})")
    return new_row[0]


def populate_user(user_id, goals_data, workouts_data, label):
    """Create goals + workouts for one user if they don't already have any."""
    db = SessionLocal()
    try:
        existing_count = db.query(Goal).filter(Goal.userid == user_id).count()
        if existing_count > 0:
            print(f"  [SKIP] {label} already has {existing_count} goal(s) — not duplicating")
            return

        # Insert goals (flush to get IDs without committing yet)
        goal_objects = []
        for g in goals_data:
            goal = Goal(
                goalname=g['goalname'],
                goaldesc=g['goaldesc'],
                estimated_workouts=g['estimated_workouts'],
                userid=user_id,
                creationdate=g['creationdate'],
                lastupdated=g['creationdate'],
                enddate=g.get('enddate'),
            )
            db.add(goal)
            db.flush()
            goal_objects.append(goal)
            print(f"  [CREATED] Goal '{g['goalname']}' (estimated: {g['estimated_workouts']} workouts)")

        db.commit()
        for g in goal_objects:
            db.refresh(g)

        # Insert workouts
        for w in workouts_data:
            db.add(Workout(
                user_id=user_id,
                goal_id=goal_objects[w['goal_idx']].id,
                date=today - timedelta(days=w['days_ago']),
                notes=w['notes'],
            ))
        db.commit()
        print(f"  [CREATED] {len(workouts_data)} workout(s)")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Fitness Tracker — Dummy Data Population Script")
    print("=" * 55)

    print("\n[1/4] Ensuring schema is up to date...")
    ensure_column()
    print("  [OK] Goals.estimated_workouts column")

    print("\n[2/4] Creating test users...")
    with engine.begin() as conn:
        jp_id   = get_or_create_user(conn, TEST_USERS[0])
        alex_id = get_or_create_user(conn, TEST_USERS[1])

    print(f"\n[3/4] Populating JP's data (user_id={jp_id})...")
    populate_user(jp_id, JP_GOALS, JP_WORKOUTS, 'JP')

    print(f"\n[4/4] Populating Alex's data (user_id={alex_id})...")
    populate_user(alex_id, ALEX_GOALS, ALEX_WORKOUTS, 'Alex')

    print("\n" + "=" * 55)
    print("  Done! Test credentials:")
    print("    jp@test.com   / password123  (3 goals, 15 workouts)")
    print("    alex@test.com / password123  (2 goals,  5 workouts)")
    print("=" * 55)


if __name__ == "__main__":
    main()
