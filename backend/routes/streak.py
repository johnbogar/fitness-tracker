from flask import Blueprint, jsonify, session
from db import conn
from sqlalchemy import text
from datetime import date, timedelta

streak_bp = Blueprint('streak', __name__)

@streak_bp.route('/api/streak', methods=['GET'])
def get_streak():
    """
    Calculate current and longest workout streaks for the logged-in user.
    A streak = consecutive calendar days with at least one workout logged.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']

    # Fetch all distinct workout dates for user, sorted ascending
    rows = conn.execute(
        text('SELECT DISTINCT date FROM "Workouts" WHERE user_id = :uid ORDER BY date ASC'),
        {'uid': user_id}
    ).fetchall()

    if not rows:
        return jsonify({'currentStreak': 0, 'longestStreak': 0})

    workout_dates = [row[0] for row in rows]  # list of date objects

    # Calculate longest streak
    longest = 1
    current_run = 1
    for i in range(1, len(workout_dates)):
        if workout_dates[i] == workout_dates[i - 1] + timedelta(days=1):
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    # Calculate current streak (streak ending today or yesterday)
    today = date.today()
    current_streak = 0
    if workout_dates[-1] >= today - timedelta(days=1):
        current_streak = 1
        for i in range(len(workout_dates) - 2, -1, -1):
            if workout_dates[i + 1] == workout_dates[i] + timedelta(days=1):
                current_streak += 1
            else:
                break

    return jsonify({
        'currentStreak': current_streak,
        'longestStreak': longest
    })