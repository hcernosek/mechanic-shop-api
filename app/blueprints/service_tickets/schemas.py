
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.blueprints.mechanics.schemas import MechanicSchema
from app.blueprints.inventory.schemas import InventorySchema
from app.extensions import ma
from app.models import ServiceTicket, ServiceInventory
from marshmallow import fields, validates_schema, ValidationError


class ServiceInventoryInputSchema(ma.Schema):
    inventory_id = fields.Int(required=True)
    quantity = fields.Int(required=True)


class ServiceInventoryOutputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceInventory
        include_fk = True
        load_instance = True
        include_relationships = True
        exclude = ("service_ticket",)

    inventory = fields.Nested(lambda: InventorySchema(only=("id", "name", "price")))


class TicketCreateSchema(ma.Schema):
    """
    Handles creation of ServiceTickets with related mechanic and inventory assignments.
    JSON input Example:
    {
        "vin": "1HGCM82633A123456",
        "service_date": "2025-11-08",
        "service_desc": "Oil and filter change",
        "customer_id": 1,
        "mechanic_ids": [1, 2, 3],
        "inventory": [
            {"inventory_id": 2, "quantity": 1},
            {"inventory_id": 5, "quantity": 3}
        ]
    }
    """

    # id = fields.Int(dump_only=True)
    vin = fields.Str(required=True)
    service_date = fields.Date(required=True)
    service_desc = fields.Str(required=True)
    customer_id = fields.Int(required=True)
    mechanic_ids = fields.List(fields.Int(), required=False)
    inventory = fields.List(fields.Nested(ServiceInventoryInputSchema), required=False)

    @validates_schema
    def validate_inventory(self, data, **kwargs):
        inv = data.get("inventory", [])

        if not isinstance(inv, list):
            raise ValidationError("Inventory must be a list of Inventory objects")
        
        for item in inv:
            if "inventory_id" not in item:
                raise ValidationError("Each inventory entry requires an inventory_id")


class TicketReturnSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ServiceTicket
        include_fk = True
        load_instance = True
        include_relationships = True

    vin = fields.Str()
    service_date = fields.Date()
    service_desc = fields.Str()
    customer_id = fields.Int()
    mechanics = fields.List(fields.Nested(MechanicSchema(only=("id","name"))))
    service_inventory = fields.List(fields.Nested(ServiceInventoryOutputSchema))


class TicketAssignMechanicSchema(ma.Schema):
    add_mechanics_ids = fields.List(fields.Int(), required=True)

    class Meta:
        fields = ('add_mechanics_ids',)


class TicketRemoveMechanicSchema(ma.Schema):
    remove_mechanics_ids = fields.List(fields.Int(), required=True)

    class Meta:
        fields = ('remove_mechanics_ids',)


# # Addition of Schema for Inventory Assignment to Service Tickets

# class ServiceTicketAssignInventorySchema(ma.Schema):
#     add_inventory_items = fields.Nested("InventoryQuantitySchema", many=True)

#     class Meta:
#         fields = ('add_inventory_items',)


ticket_create_schema = TicketCreateSchema()
ticket_return_schema = TicketReturnSchema()
tickets_return_schema = TicketReturnSchema(many=True)

ticket_assign_mechanic_schema = TicketAssignMechanicSchema()
ticket_remove_mechanic_schema = TicketRemoveMechanicSchema()

# service_ticket_assign_inventory_schema = ServiceTicketAssignInventorySchema()

