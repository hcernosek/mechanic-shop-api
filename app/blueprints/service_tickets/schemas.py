
from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields

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


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True) 