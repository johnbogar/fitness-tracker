from flask import Flask, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from routes.goals import goals_bp
from routes.auth import auth_bp  
from routes.add_goal import add_goal_bp
from routes.delete_goal import delete_goal_bp
from routes.dashboard import dashboard_bp
from routes.log_workout import log_workout_bp
from routes.edit_goal import edit_goal_bp
from routes.dashboard import dashboard_bp
from routes.log_workout import log_workout_bp
from routes.streak import streak_bp
from routes.personal_records import personal_records_bp
from routes.edit_user import edit_user_bp
from routes.reset_password import reset_password_bp
from db import db_bp
from datetime import timedelta

# Load environment variables
load_dotenv()

# start backend in terminal in backend directory using 'python app.py'
app = Flask(__name__)

# NEW: Configure session for login/logout
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configure CORS to allow credentials (needed for sessions/cookies)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# register your blueprints
app.register_blueprint(goals_bp)
app.register_blueprint(auth_bp)  
app.register_blueprint(add_goal_bp)
app.register_blueprint(db_bp)
app.register_blueprint(delete_goal_bp)
app.register_blueprint(edit_goal_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(log_workout_bp)
app.register_blueprint(streak_bp)
app.register_blueprint(personal_records_bp)
app.register_blueprint(edit_user_bp)
app.register_blueprint(reset_password_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)