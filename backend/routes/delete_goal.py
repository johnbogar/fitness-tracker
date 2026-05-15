from flask import Blueprint, request, jsonify, session
from db import SessionLocal
from models.goal import Goal

delete_goal_bp = Blueprint("delete_goal", __name__)

@delete_goal_bp.route('/api/delete_goal', methods=["POST"])
def delete_goal():
    """
    Function to delete a goal
    :return: json of the goal deleted
    :errors:  none
    """
    # get request data
    data = request.get_json(silent=True)
    
    # make sure exists
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    # check user logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # get current user id from session
    user_id = session['user_id']
    user_id = int(user_id)

    # get data from request
    goal_id = data.get("goalId")

    try:
        # connect to session
        db = SessionLocal()

        # find the users goal
        goal = db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.userid == user_id
        ).first()

        # make sure the goal exists
        if not goal:
            return jsonify({"error": "Goal not found"}), 404

        # delete specified goal
        db.delete(goal)
        db.commit()

        return jsonify({
            "message": "Goal deleted successfully",
            "deletedGoalId": goal_id
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        db.close()