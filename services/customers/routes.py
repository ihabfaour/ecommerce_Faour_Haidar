from flask import Blueprint, request, jsonify
from .models import User
from database.db_config import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import bcrypt

user_bp = Blueprint('user', __name__)


# Helper function to check the role
def check_role(expected_role):
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user or user.role != expected_role:
        return jsonify({"error": "Access forbidden"}), 403
    return None

@user_bp.route('/register', methods=['POST'])
def register_customer():
    try:
        data = request.json
        # Check if username exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400

        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        new_customer = User(
            full_name=data['full_name'],
            username=data['username'],
            password=hashed_password.decode('utf-8'),
            age=data['age'],
            address=data['address'],
            gender=data['gender'],
            marital_status=data['marital_status'],
            role=data.get('role', 'customer')  # Defaults to 'customer'
        )

        db.session.add(new_customer)
        db.session.commit()
        
        access_token = create_access_token(identity=data['username'], expires_delta=timedelta(hours=24))

        return jsonify({"message": "User registered successfully","token": access_token}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login_customer():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Find the user by username
        customer = User.query.filter_by(username=username).first()
        if not customer:
            return jsonify({"error": "Invalid username or password"}), 401

        # Check password
        if not bcrypt.checkpw(password.encode('utf-8'), customer.password.encode('utf-8')):
            return jsonify({"error": "Invalid username or password"}), 401

        # Generate JWT Token
        access_token = create_access_token(identity=username, expires_delta=timedelta(hours=24))

        return jsonify({"message": "Login successful", "token": access_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_customer():
    auth_error = check_role('customer')  # Only customers can delete themselves
    if auth_error:
        return auth_error
    try:
        # Get the currently logged-in user's identity
        current_user = get_jwt_identity()

        # Query the customer by username
        customer = User.query.filter_by(username=current_user).first()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Delete the customer
        db.session.delete(customer)
        db.session.commit()

        return jsonify({"message": f"Customer {current_user} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@user_bp.route('/update', methods=['PATCH'])
@jwt_required()
def update_customer():
    auth_error = check_role('customer')  
    if auth_error:
        return auth_error
    
    try:
        # Get the currently logged-in user's identity
        current_user = get_jwt_identity()

        # Query the customer by username
        customer = User.query.filter_by(username=current_user).first()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Update fields from JSON payload
        data = request.json
        if "full_name" in data:
            customer.full_name = data["full_name"]
        if "password" in data:
            hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())
            customer.password = hashed_password.decode('utf-8')
        if "age" in data:
            customer.age = data["age"]
        if "address" in data:
            customer.address = data["address"]
        if "gender" in data:
            customer.gender = data["gender"]
        if "marital_status" in data:
            customer.marital_status = data["marital_status"]

        # Save changes
        db.session.commit()
        return jsonify({"message": "Customer updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@user_bp.route('/', methods=['GET'])
def get_all_customers():
    try:
        # Query all users
        users = User.query.all()

        # Serialize the result
        result = [
            {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "age": user.age,
                "address": user.address,
                "gender": user.gender,
                "marital_status": user.marital_status,
                "wallet_balance": float(user.wallet_balance),
            }
            for user in users
        ]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer_by_id(customer_id):
    try:
        # Query the customer by ID
        user = User.query.get(customer_id)

        if not user:
            return jsonify({"error": "Customer not found"}), 404

        # Serialize the result
        result = {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "age": user.age,
            "address": user.address,
            "gender": user.gender,
            "marital_status": user.marital_status,
            "wallet_balance": float(user.wallet_balance),
        }

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/wallet/charge', methods=['POST'])
@jwt_required()
def charge_wallet():
    auth_error = check_role('customer')  
    if auth_error:
        return auth_error
    try:
        # Get the currently logged-in user's identity
        current_user = get_jwt_identity()

        # Query the customer by username
        customer = User.query.filter_by(username=current_user).first()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Get the amount to charge from the request
        data = request.json
        amount = data.get("amount")

        if not amount or amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        # Update wallet balance
        customer.wallet_balance += amount
        db.session.commit()

        return jsonify({"message": f"${amount} successfully added to wallet", 
                        "wallet_balance": float(customer.wallet_balance)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@user_bp.route('/wallet/deduct', methods=['POST'])
@jwt_required()
def deduct_wallet():
    auth_error = check_role('customer')  
    if auth_error:
        return auth_error
    try:
        # Get the currently logged-in user's identity
        current_user = get_jwt_identity()

        # Query the customer by username
        customer = User.query.filter_by(username=current_user).first()

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Get the amount to deduct from the request
        data = request.json
        amount = data.get("amount")

        if not amount or amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        if customer.wallet_balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        # Deduct amount from wallet balance
        customer.wallet_balance -= amount
        db.session.commit()

        return jsonify({"message": f"${amount} successfully deducted from wallet", 
                        "wallet_balance": float(customer.wallet_balance)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

