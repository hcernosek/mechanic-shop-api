from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema
from app.models import ServiceTicket, Mechanic, Customer, db
from sqlalchemy.exc import IntegrityError
from app.blueprints.service_tickets import service_tickets_bp
 

# create a new service ticket
@service_tickets_bp.route("/", methods=['POST'])
def create_service_ticket():
    try:
        ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # validate customer exists
    customer_id = ticket_data.get('customer_id')
    if not customer_id:
        return jsonify({'error': 'customer_id is required'}), 400

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({'error': f'Customer with id {customer_id} not found'}), 400

    new_ticket = ServiceTicket(
        vin=ticket_data['vin'],
        service_date=ticket_data['service_date'],
        service_desc=ticket_data['service_desc'],
        customer_id=customer_id,
    )

    mechanic_ids = ticket_data.get('mechanics') or []
    # if a single int was sent (not a list), normalize to list
    if isinstance(mechanic_ids, int):
        mechanic_ids = [mechanic_ids]

    for mechanic_id in mechanic_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({'error': f'Invalid mechanic ID: {mechanic_id}'}), 400
        new_ticket.mechanics.append(mechanic)

    db.session.add(new_ticket)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database integrity error', 'details': str(e.orig)}), 400

    return service_ticket_schema.jsonify(new_ticket), 201



# Get all service ticket

@service_tickets_bp.route("/", methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets)

# Get a specific service_ticket (by ID)

@service_tickets_bp.route("/<int:service_ticket_id>", methods=['GET'])
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if service_ticket:
        return service_ticket_schema.jsonify(service_ticket), 200
    return jsonify({"error": "Service Ticket not found."}), 404

# Update a specific service_ticket (by ID) 

@service_tickets_bp.route("/<int:service_ticket_id>", methods=['PUT'])
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404
    
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in service_ticket_data.items():
        setattr(service_ticket, key, value)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200

# Delete a specific service_ticket (by ID)

@service_tickets_bp.route("/<int:service_ticket_id>", methods=['DELETE'])
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404
    
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": f'Service Ticket id: {service_ticket_id}, successfully deleted.'}), 200