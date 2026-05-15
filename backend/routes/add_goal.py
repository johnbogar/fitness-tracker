from flask import Blueprint, request, jsonify, session
from db import SessionLocal
from models.goal import Goal
from datetime import datetime

add_goal_bp = Blueprint("add_goal", __name__)

@add_goal_bp.route('/api/add_goal', methods=["POST"])
def create_goal():
    """
    Function to create a goal using the Goal table model
    :return: json of the goal added and the response
    :errors:  if goal and user id dont exist or fails to add to db
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # get data from request
    goal_name = data.get("goalName")
    goal_desc = data.get("goalDesc", "")
    end_date = data.get("endDate")
    estimated_workouts = data.get("estimatedWorkouts", 10)

    # check user logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # get current user id from session
    user_id = session['user_id']
    user_id = int(user_id)

    # check data exists
    if goal_name is None or user_id is None:
        return jsonify({"error": "goal_name and user_id are required"}), 400
    
    # validate data
    if not isinstance(goal_name, str):
        return jsonify({"error": "Invalid input"}), 400

    if len(goal_name) > 255:
        return jsonify({"error": "Too long"}), 400

    if not isinstance(goal_desc, str):
        return jsonify({"error": "Invalid input"}), 400

    if len(goal_desc) > 255:
        return jsonify({"error": "Too long"}), 400

    # validate estimated_workouts
    if not isinstance(estimated_workouts, int) or estimated_workouts < 1:
        return jsonify({"error": "estimatedWorkouts must be a positive integer"}), 400

    try:
        # create a new goal
        new_goal = Goal(
            goalname=goal_name,
            goaldesc=goal_desc,
            userid=user_id,
            enddate=datetime.strptime(end_date, "%Y-%m-%d") if end_date else None,
            estimated_workouts=estimated_workouts
        )

        # connect to session
        db = SessionLocal()

        # add to the database
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)

        return jsonify({
            "id": new_goal.id,
            "goalname": new_goal.goalname,
            "goaldesc": new_goal.goaldesc,
            "creationdate": new_goal.creationdate,
            "lastupdated": new_goal.lastupdated,
            "enddate": new_goal.enddate,
            "userid": new_goal.userid,
            "estimated_workouts": new_goal.estimated_workouts
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        db.close()