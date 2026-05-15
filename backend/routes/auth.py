from flask import Blueprint, jsonify, request, session
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from db import conn

# Create auth blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route('/api/login', methods=["POST"])
def login():
    """
    Log in an existing user
    
    Request body:
        {
            "email": "john@example.com",
            "password": "securePassword123"
        }
    
    Returns:
        200: Login successful, session created
        400: Missing fields
        401: Invalid credentials
        500: Server error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Query user by email
        query = text('SELECT id, firstname, lastname, email, password FROM "Users" WHERE email = :email;')
        result = conn.execute(query, {"email": email}).fetchone()

        # Check if user exists
        if not result:
            return jsonify({'error': 'Invalid email or password'}), 401

        user_id, firstname, lastname, user_email, password_hash = result
        name = f"{firstname} {lastname}"
        
        # Verify password
        if not check_password_hash(password_hash, password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create session
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = user_email
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user_id,
                'name': name,
                'email': user_email
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500


@auth_bp.route('/api/register', methods=["POST"])
def register():
    """
    Register a new user

    Request body:
        {
            "firstname": "John",
            "lastname": "Doe",
            "email": "john@example.com",
            "password": "securePassword123"
        }

    Returns:
        201: Account created successfully
        400: Missing or invalid fields
        409: Email already in use
        500: Server error
    """
    try:
        data = request.get_json()

        # Validate all fields present
        if not all([data.get('firstname'), data.get('lastname'), data.get('email'), data.get('password')]):
            return jsonify({'error': 'All fields are required'}), 400

        firstname = data['firstname'].strip()
        lastname = data['lastname'].strip()
        email = data['email'].strip().lower()
        password = data['password']

        # Basic email format check
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400

        # Check for duplicate email
        check_query = text('SELECT id FROM "Users" WHERE email = :email;')
        existing = conn.execute(check_query, {"email": email}).fetchone()
        if existing:
            return jsonify({'error': 'An account with the following email already exists'}), 409

        # Hash password and insert new user
        hashed_password = generate_password_hash(password)
        insert_query = text(
            'INSERT INTO "Users" (firstname, lastname, email, password, creationdate) '
            'VALUES (:firstname, :lastname, :email, :password, NOW());'
        )
        conn.execute(insert_query, {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "password": hashed_password
        })
        conn.commit()

        return jsonify({'message': 'Account created successfully'}), 201

    except Exception as e:
        print(f"Register error: {str(e)}")
        return jsonify({'error': 'Server error occurred'}), 500


@auth_bp.route('/api/logout', methods=["POST"])
def logout():
    """
    Log out the current user
    
    Returns:
        200: Logout successful
    """
    # Clear session
    session.clear()
    
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/api/check-auth', methods=["GET"])
def check_auth():
    """
    Check if user is currently authenticated
    
    Returns:
        200: User is authenticated with user info
        401: User is not authenticated
    """
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'name': session['user_name'],
                'email': session['user_email']
            }
        }), 200
    else:
        return jsonify({'authenticated': False}), 401