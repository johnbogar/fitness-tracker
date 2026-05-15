"""
Workout routes - handles CRUD operations for workouts
"""
from flask import Blueprint, request, jsonify, session
from datetime import date, datetime
from models.workout import Workout
from db import SessionLocal

log_workout_bp = Blueprint('log_workout', __name__)


@log_workout_bp.route('/api/log_workout', methods=["POST"])
def log_workout():
    """Create a new workout"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = int(session['user_id'])
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Extract and validate inputs
    goal_id = data.get("goalId")
    date_str = data.get("date")
    notes = data.get("notes", "")

    # Validate notes
    if not isinstance(notes, str):
        return jsonify({"error": "Invalid input: notes must be a string"}), 400
    
    if len(notes) > 1000:
        return jsonify({"error": "Notes too long (max 1000 characters)"}), 400

    # Parse date
    workout_date = date.today()
    if date_str:
        try:
            workout_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Validate goal_id
    if goal_id is not None and not isinstance(goal_id, int):
        return jsonify({"error": "Invalid goalId"}), 400

    # Create and save workout
    db = SessionLocal()
    try:
        new_workout = Workout(
            user_id=user_id,
            goal_id=goal_id,
            date=workout_date,
            notes=notes
        )

        db.add(new_workout)
        db.commit()
        db.refresh(new_workout)

        return jsonify({
            "id": new_workout.id,
            "user_id": new_workout.user_id,
            "goal_id": new_workout.goal_id,
            "date": str(new_workout.date),
            "notes": new_workout.notes,
            "created_at": str(new_workout.created_at)
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@log_workout_bp.route('/api/workouts', methods=["GET"])
def get_workouts():
    """Get all workouts for the logged-in user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = int(session['user_id'])
    db = SessionLocal()

    try:
        workouts = (
            db.query(Workout)
            .filter(Workout.user_id == user_id)
            .order_by(Workout.date.desc())
            .all()
        )

        return jsonify([
            {
                "id": w.id,
                "goal_id": w.goal_id,
                "date": str(w.date),
                "notes": w.notes,
                "created_at": str(w.created_at)
            }
            for w in workouts
        ]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@log_workout_bp.route('/api/workout/<int:workout_id>', methods=['PUT'])
def edit_workout(workout_id):
    """Update an existing workout"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = int(session['user_id'])
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    db = SessionLocal()
    try:
        # Find workout - CRITICAL: must belong to this user
        workout = db.query(Workout).filter(
            Workout.id == workout_id,
            Workout.user_id == user_id  # Security: can't edit others' workouts
        ).first()

        if not workout:
            return jsonify({'error': 'Workout not found'}), 404

        # Validate and update notes if provided
        if 'notes' in data:
            notes = data['notes']
            if not isinstance(notes, str):
                return jsonify({"error": "Invalid input: notes must be a string"}), 400
            if len(notes) > 1000:
                return jsonify({"error": "Notes too long (max 1000 characters)"}), 400
            workout.notes = notes

        # Validate and update date if provided
        if 'date' in data:
            date_str = data['date']
            try:
                workout.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Validate and update goal_id if provided
        if 'goalId' in data:
            goal_id = data['goalId']
            if goal_id is not None and not isinstance(goal_id, int):
                return jsonify({"error": "Invalid goalId"}), 400
            workout.goal_id = goal_id

        # Save changes
        db.commit()
        db.refresh(workout)

        return jsonify({
            "id": workout.id,
            "user_id": workout.user_id,
            "goal_id": workout.goal_id,
            "date": str(workout.date),
            "notes": workout.notes,
            "created_at": str(workout.created_at)
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@log_workout_bp.route('/api/workout/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    """Delete a workout"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = int(session['user_id'])
    db = SessionLocal()

    try:
        # Find workout - CRITICAL: must belong to this user
        workout = db.query(Workout).filter(
            Workout.id == workout_id,
            Workout.user_id == user_id  # Security: can't delete others' workouts
        ).first()

        if not workout:
            return jsonify({'error': 'Workout not found'}), 404

        # Delete it
        db.delete(workout)
        db.commit()

        return jsonify({'message': 'Workout deleted successfully'}), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()