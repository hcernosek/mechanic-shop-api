
from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields

  # Example of schema from dylan at coding temple

    # mechanics = fields.Nested('MechanicSchema', many=True)
    # customer = fields.Nested('CustomerSchema')
    # class Meta:
    #     model = ServiceTicket
    #     fields = ('mechanic_ids', 'vin','service_date', 'service_desc', 'customer_id', 'mechanics', 'customer', 'id')


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        # Do not auto-create a SQLAlchemy model instance during load.
        # Return a plain dict so the route can construct the model and
        # resolve relationship IDs (mechanics) manually.
        load_instance = False
        include_fk = True
        
    id = fields.Int(dump_only=True)
    vin = fields.Str(required=True)
    service_date = fields.Date(required=True)
    service_desc = fields.Str(required=True)       
    # Allow customer_id to be both loaded and dumped so responses include it
    customer_id = fields.Int(required=True)

    # mechanics can be omitted or be a single ID or a list of IDs on input;
    # keep that as a load-only field.
    mechanics = fields.List(fields.Int(), required=False, load_only=True)

    # For responses, provide a list of mechanic IDs derived from the
    # relationship. This will show up in GET responses as `mechanic_ids`.
    mechanic_ids = fields.Method("get_mechanic_ids", dump_only=True)

    def get_mechanic_ids(self, obj):
        return [m.id for m in obj.mechanics] if getattr(obj, 'mechanics', None) else []


class ServiceTicketAssignMechanicSchema(ma.Schema):
    add_mechanics_ids = fields.List(fields.Int(), required=True)

    class Meta:
        fields = ('add_mechanics_ids',)


class ServiceTicketRemoveMechanicSchema(ma.Schema):
    remove_mechanics_ids = fields.List(fields.Int(), required=True)

    class Meta:
        fields = ('remove_mechanics_ids',)

# Addition of Schema for Inventory Assignment to Service Tickets

class ServiceTicketAssignInventorySchema(ma.Schema):
    add_inventory_items = fields.Nested("InventoryQuantitySchema", many=True)

    class Meta:
        fields = ('add_inventory_items',)

class InventoryQuantitySchema(ma.Schema):
    item_id = fields.Int(required=True)
    quantity = fields.Int(required=True)



service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True) 
service_ticket_assign_mechanic_schema = ServiceTicketAssignMechanicSchema()
service_ticket_remove_mechanic_schema = ServiceTicketRemoveMechanicSchema()
service_ticket_assign_inventory_schema = ServiceTicketAssignInventorySchema()




