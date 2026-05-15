from flask import Blueprint, request, jsonify, session
from db import conn
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

reset_password_bp = Blueprint("reset-password", __name__)

@reset_password_bp.route('/api/reset-password', methods=["PUT"])
def reset_password():
    """
    Reset logged-in user's password
    """

    try:
        # check login
        if 'user_id' not in session:
            return jsonify({'error': 'User not authenticated'}), 401

        data = request.get_json()

        # validate required fields
        if not data or not data.get('currentPassword') or not data.get('newPassword'):
            return jsonify({'error': 'All fields are required'}), 400

        current_password = data['currentPassword']
        new_password = data['newPassword']
        user_id = session['user_id']

        # password rules
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        # get user from DB
        get_query = text('SELECT id, password FROM "Users" WHERE id = :id;')
        user = conn.execute(get_query, {"id": user_id}).fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        stored_password = user.password

        # check current password
        if not check_password_hash(stored_password, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401

        # hash new password
        hashed_password = generate_password_hash(new_password)

        # update password
        update_query = text(
            'UPDATE "Users" SET password = :password WHERE id = :id;'
        )

        conn.execute(update_query, {
            "password": hashed_password,
            "id": user_id
        })

        conn.commit()

        return jsonify({
            "message": "Password updated successfully"
        }), 200

    except Exception as e:
        print(f"Reset password error: {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500