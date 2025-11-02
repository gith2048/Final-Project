from flask import Blueprint, request, jsonify, session
from models.user import User
from db import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400
    user = User(name=data['name'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        session["user_email"] = user.email  # ✅ Store email in session
        return jsonify({
            "message": "Login successful",
            "user": {
                "name": user.name,
                "email": user.email
            }
        })
    return jsonify({"error": "Invalid credentials"}), 401