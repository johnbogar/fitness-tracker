from flask import Blueprint, jsonify, session
from sqlalchemy import text
from db import conn

# make a ablueprint of goals
goals_bp = Blueprint("goals", __name__)

@goals_bp.route('/api/view_goals', methods=["GET"])

def get_goals():
    """
    Function for getting the goals from the databse
    :returns: jsonify(goals): the goals as jsosn
    """
    try:
        # check user logged in
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # get current user id from session
        user_id = session['user_id']
        user_id = int(user_id)

        # query
        query = text('SELECT * FROM "Goals" WHERE userid = :userid;')
        result = conn.execute(query,{"userid": user_id}).fetchall()

        goals = [dict(row._mapping) for row in result]
        return jsonify(goals)
    except Exception as e:
        conn.rollback()  
        return jsonify({"error": str(e)}), 500