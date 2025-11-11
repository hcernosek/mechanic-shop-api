from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.blueprints.service_tickets.schemas import ticket_create_schema, ticket_return_schema, tickets_return_schema, ticket_assign_mechanic_schema, ticket_remove_mechanic_schema
from app.models import ServiceTicket, Mechanic, ServiceInventory, Inventory, db
from app.blueprints.service_tickets import service_tickets_bp
 
# ======================================================================
# CREATE A SERVICE TICKET [POST]
# ======================================================================

@service_tickets_bp.route("/", methods=['POST'])
def create_service_ticket():
    try:
        # Log the incoming request data for debugging
        print('Request:', request.json)
        ticket_data = ticket_create_schema.load(request.json)
        
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_ticket = ServiceTicket(
        vin=ticket_data['vin'],
        service_date=ticket_data['service_date'],
        service_desc=ticket_data['service_desc'],
        customer_id=ticket_data['customer_id'],
    )

    db.session.add(new_ticket)
    db.session.flush() # Flush to get the new_ticket.id before committing

    # if request contains mechanic_ids
    if 'mechanic_ids' in ticket_data and ticket_data['mechanic_ids']: # if mechanic_ids is in request and the list is not empty
        query = select(Mechanic).where(Mechanic.id.in_(ticket_data['mechanic_ids']))
        
        # returns a list of Mechanics ORM objects and and adds each to the new_ticket with .extend() method
        mechanics = db.session.scalars(query).all()
        new_ticket.mechanics.extend(mechanics)

    # if request contains inventory
    if 'inventory' in ticket_data and ticket_data['inventory']:
        
        # iterate over each inventory item in request as 'item' used to assign quantity
        for item in ticket_data['inventory']:
            inventory_data = db.session.get(Inventory, item['inventory_id'])
            
            # if inventory item cannot be found, rollback current transaction and return error
            if not inventory_data:
                db.session.rollback()
                return jsonify({'error': f'Invalid inventory ID: {item["inventory_id"]}'}), 400
            
            added_inventory = ServiceInventory(
                ticket_id=new_ticket.id, # uses the new_ticket.id obtained from flush()
                inventory_id=inventory_data.id,
                quantity=item['quantity'] # quantity from the request 
            )
            db.session.add(added_inventory)

    # Commit service tickets with all additions 
    db.session.commit()
    return jsonify({
        "message": "Service Ticket created successfully",
        "service_ticket": ticket_return_schema.dump(new_ticket)
    }), 201

# How is the mapping of inventory_items and mechanic_ids different (since one is handled as a association table and the other is a object)?


# ======================================================================
# GET ALL SERVICE TICKET [GET]
# ======================================================================

@service_tickets_bp.route("/", methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    service_tickets = db.session.execute(query).scalars().all()

    return tickets_return_schema.jsonify(service_tickets)


# ======================================================================
# GET A SPECIFIC SERVICE TICKET BY ID [GET]
# ======================================================================

@service_tickets_bp.route("/<int:ticket_id>", methods=['GET'])
def get_service_ticket(ticket_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)

    if service_ticket:
        return ticket_return_schema.jsonify(service_ticket), 200
    return jsonify({"error": "Service Ticket not found."}), 404


# ======================================================================
# DELETE A SERVICE TICKET [DELETE]
# ======================================================================

# @service_tickets_bp.route("/<int:ticket_id>", methods=['DELETE'])
# def delete_service_ticket(ticket_id):
#     query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
#     service_ticket = db.session.execute(query).scalar_one_or_none()

#     if not service_ticket:
#         return jsonify({"error": "Service Ticket not found."}), 404
    
#     db.session.delete(service_ticket)
#     db.session.commit()
#     return jsonify({"message": f'Service Ticket id: {ticket_id}, successfully deleted.'}), 200


# ======================================================================
# ASSIGN MECHANICS TO A SERVICE TICKET [PUT]
# ======================================================================

@service_tickets_bp.route("/<int:ticket_id>/assign_mechanics", methods=['PUT'])
def assign_mechanics_service_ticket(ticket_id):
    try:
        assign_mechanics = ticket_assign_mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    service_ticket = db.session.execute(query).scalar_one_or_none()

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404
    
    for mechanic_id in assign_mechanics['add_mechanics_ids']:
        query_mechanic = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query_mechanic).scalar_one_or_none()

        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    db.session.commit()
    return ticket_return_schema.jsonify(service_ticket), 200


# ======================================================================
# REMOVE MECHANICS FROM A SERVICE TICKET [PUT]
# ======================================================================

@service_tickets_bp.route("/<int:ticket_id>/remove_mechanics", methods=['PUT'])
def remove_mechanics_service_ticket(ticket_id):
    try:
        remove_mechanics = ticket_remove_mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
    service_ticket = db.session.execute(query).scalar_one_or_none()

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404
    
    for mechanic_id in remove_mechanics['remove_mechanics_ids']:
        query_mechanic = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query_mechanic).scalar_one_or_none()

        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    db.session.commit()
    return ticket_return_schema.jsonify(service_ticket), 200


# ======================================================================
# ASSIGN INVENTORY TO A SERVICE TICKET [PUT]
# ======================================================================

# @service_tickets_bp.route("/<int:ticket_id>/assign_inventory", methods=['PUT'])
# def assign_inventory_service_ticket(ticket_id):
#     try:
#         assign_inventory = service_ticket_assign_inventory_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400

#     query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
#     service_ticket = db.session.execute(query).scalar_one_or_none()

#     if not service_ticket:
#         return jsonify({"error": "Service Ticket not found."}), 404
    
#     for inventory_items in assign_inventory['add_inventory_items']:
#         query_mechanic = select(Mechanic).where(Mechanic.id == mechanic_id)
#         mechanic = db.session.execute(query_mechanic).scalar_one_or_none()

#         if mechanic and mechanic not in service_ticket.mechanics:
#             service_ticket.mechanics.append(mechanic)

#     db.session.commit()
#     return ticket_return_schema.jsonify(service_ticket), 200