from flask import Blueprint, request, jsonify, session
from db import SessionLocal
from models.goal import Goal
from datetime import datetime

edit_goal_bp = Blueprint("edit_goal", __name__)

@edit_goal_bp.route('/api/edit_goal', methods=["PUT"])
def edit_goal():
    """
    Function to edit an existing goal
    """

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # get data
    goal_id = data.get("goalId")
    goal_name = data.get("goalName")
    goal_desc = data.get("goalDesc", "")
    end_date = data.get("endDate")
    estimated_workouts = data.get("estimatedWorkouts")

    # check logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = int(session['user_id'])

    # validate required fields
    if goal_id is None or goal_name is None:
        return jsonify({"error": "goalId and goalName are required"}), 400

    # validate types
    if not isinstance(goal_name, str) or not isinstance(goal_desc, str):
        return jsonify({"error": "Invalid input"}), 400

    if len(goal_name) > 255 or len(goal_desc) > 255:
        return jsonify({"error": "Too long"}), 400

    if estimated_workouts is not None:
        if not isinstance(estimated_workouts, int) or estimated_workouts < 1:
            return jsonify({"error": "estimatedWorkouts must be a positive integer"}), 400

    db = SessionLocal()

    try:
        # get existing goal
        goal = db.query(Goal).filter(Goal.id == goal_id).first()

        if not goal:
            return jsonify({"error": "Goal not found"}), 404

        # ownership check
        if goal.userid != user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # update fields
        goal.goalname = goal_name
        goal.goaldesc = goal_desc
        goal.enddate = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        if estimated_workouts is not None:
            goal.estimated_workouts = estimated_workouts

        # auto updates lastupdated in goal model
        db.commit()
        db.refresh(goal)

        return jsonify({
            "message": "Goal updated successfully",
            "goal": {
                "id": goal.id,
                "goalname": goal.goalname,
                "goaldesc": goal.goaldesc,
                "creationdate": goal.creationdate,
                "lastupdated": goal.lastupdated,
                "enddate": goal.enddate,
                "userid": goal.userid,
                "estimated_workouts": goal.estimated_workouts
            }
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        db.close()