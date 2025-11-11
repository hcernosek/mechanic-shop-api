
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema, top_mechanics_schema
from app.models import Mechanic, db
from app.blueprints.mechanics import mechanics_bp
from app.extensions import limiter

# ======================================================================
# CREATE A NEW MECHANIC [POST]
# ======================================================================

@mechanics_bp.route("/", methods=['POST'])
@limiter.limit("5 per hour")  #A client can only attempt to make 5 users per hour
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data['email']) #Checking our db for a mechanic with this email
    existing_mechanic = db.session.execute(query).scalars().all()
    if existing_mechanic:
        return jsonify({"error": "Email already associated with a mechanic."}), 400
    
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


# ======================================================================
# GET ALL MECHANICS [GET]
# ======================================================================

@mechanics_bp.route("/", methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)


# ======================================================================
# GET A SPECIFIC MECHANIC [GET]
# ======================================================================

@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404


# ======================================================================
# UPDATE A MECHANIC ENTRY[PUT]
# ======================================================================

@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "mechanic not found."}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# ======================================================================
# DELETE A MECHANIC [DELETE]
# ======================================================================

@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "mechanic not found."}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f'mechanic id: {mechanic_id}, successfully deleted.'}), 200


# ======================================================================
# 
# ======================================================================

@mechanics_bp.route("/top_mechanics", methods=['GET'])
def get_top_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key=lambda mech: len(mech.service_tickets), reverse=True)

    return top_mechanics_schema.jsonify(mechanics)