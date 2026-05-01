from flask import Blueprint, request, jsonify
from backend.services.auth_service import register_admin, login_admin, forgot_password, reset_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    register_admin(data)
    return jsonify({'message': 'Account created successfully'}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    access_token, admin_data = login_admin(data)
    return jsonify({'access_token': access_token, 'admin': admin_data}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password_route():
    data = request.get_json() or {}
    forgot_password(data)
    return jsonify({'message': 'If this email exists, a reset link has been generated'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password_route():
    data = request.get_json() or {}
    reset_password(data)
    return jsonify({'message': 'Password reset successful'}), 200
