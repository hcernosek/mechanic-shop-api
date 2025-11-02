from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.blueprints.inventory.schemas import inventory_schema, inventory_many_schema
from app.models import Inventory, db
from app.blueprints.inventory import inventory_bp
 
# ======================================================================
# CREATE INVENTORY ITEM [POST]
# ======================================================================

@inventory_bp.route("/", methods=['POST'])
def create_inventory():
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Inventory).where(Inventory.name == inventory_data['name'])
    existing_inventory = db.session.execute(query).scalars().all()
    if existing_inventory:
        return jsonify({"error": "Name already associated with a inventory item."}), 400
    
    new_inventory = Inventory(**inventory_data)
    db.session.add(new_inventory)
    db.session.commit()
    return inventory_schema.jsonify(new_inventory), 201


# ======================================================================
# GET ALL INVENTORY ITEMS [GET]
# ======================================================================

@inventory_bp.route("/", methods=['GET'])
def get_all_inventory():
    query = select(Inventory)
    inventory = db.session.execute(query).scalars().all()

    return inventory_many_schema.jsonify(inventory)


# ======================================================================
# GET A SPECIFIC INVENTORY ITEMS [GET]
# ======================================================================

@inventory_bp.route("/<int:inventory_id>", methods=['GET'])
def get_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if inventory:
        return inventory_schema.jsonify(inventory), 200
    return jsonify({"error": "Inventory item not found."}), 404


# ======================================================================
# UPDATE A INVENTORY ENTRY [PUT]
# ======================================================================

@inventory_bp.route("/<int:inventory_id>", methods=['PUT'])
def update_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({"error": "Inventory not found."}), 404
    
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in inventory_data.items():
        setattr(inventory, key, value)

    db.session.commit()
    return inventory_schema.jsonify(inventory), 200


# ======================================================================
# DELETE A INVENTORY ITEM [DELETE]
# ======================================================================

@inventory_bp.route("/<int:inventory_id>", methods=['DELETE'])
def delete_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({"error": "Inventory item not found."}), 404
    
    db.session.delete(inventory)
    db.session.commit()
    return jsonify({"message": f'inventory id: {inventory_id}, successfully deleted.'}), 200

