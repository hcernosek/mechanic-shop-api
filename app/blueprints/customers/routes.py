from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from app.models import Customer, db
from app.blueprints.customers import customers_bp
from app.utils.util import encode_token, token_required

# ======================================================================
# CUSTOMER LOGIN [POST]
# ======================================================================

@customers_bp.route("/login", methods=['POST'])
def login():

    try:     
        credentials = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    email = credentials["email"]
    password = credentials["password"]

    query = select(Customer).where(Customer.email == email)

    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == password:
        token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Login successful.",
            "token": token
        }
        return jsonify(response), 200
    
    else:
        return jsonify({"message": "Invalid email or password."}), 401

# ======================================================================
# CREATE A NEW CUSTOMER [POST]
# ======================================================================

@customers_bp.route("/", methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data['email']) #Checking our db for a customer with this email
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already associated with a customer."}), 400
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


# ======================================================================
# GET ALL CUSTOMERS [GET]
# ======================================================================

@customers_bp.route("/", methods=['GET'])
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)


# ======================================================================
# GET A SPECIFIC CUSTOMER [GET]
# ======================================================================

@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404


# ======================================================================
# UPDATE A CUSTOMER ENTRY [PUT]
# ======================================================================

@customers_bp.route("/<int:customer_id>", methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# ======================================================================
# DELETE A CUSTOMERS [DELETE]
# ======================================================================

@customers_bp.route("/", methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, successfully deleted.'}), 200

