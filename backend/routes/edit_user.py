from flask import Blueprint, request, jsonify, session
from db import SessionLocal
from db import conn
from sqlalchemy import text

# Create auth blueprint
edit_user_bp = Blueprint("edit-user", __name__)

@edit_user_bp.route('/api/edit-user', methods=["PUT"])
def edit_user():
    """
    Edit an existing user's profile information
    
    Request body:
        {
            "firstname": "John",
            "lastname": "Doe",
            "email": "john@example.com"
        }
    
    Returns:
        200: User updated successfully
        400: Missing or invalid fields
        401: User not authenticated
        409: Email already in use
        500: Server error
    """
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'error': 'User not authenticated'}), 401

        data = request.get_json()

        # Validate required fields
        if not all([data.get('firstname'), data.get('lastname')]):
            return jsonify({'error': 'All fields are required'}), 400

        firstname = data['firstname'].strip()
        lastname = data['lastname'].strip()
        user_id = session['user_id']

        # Update user info
        update_query = text(
            'UPDATE "Users" SET firstname = :firstname, lastname = :lastname '
            'WHERE id = :id;'
        )
        conn.execute(update_query, {
            "firstname": firstname,
            "lastname": lastname,
            "id": user_id
        })
        conn.commit()

        # Update session info
        session['user_name'] = f"{firstname} {lastname}"

        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user_id,
                'name': session['user_name'],
            }
        }), 200

    except Exception as e:
        print(f"Edit user error: {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500