
from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = False
        include_fk = True
        fields = ('id', 'name', 'email', 'phone', 'salary')
    
    # Explicitly declare fields to match model's case
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    phone = fields.Str(required=True)
    salary = fields.Float(required=True)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
