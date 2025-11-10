
from app.extensions import ma
from app.models import Inventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory

# When using auto schema, why do I not need to specify the primary key as dump_only? 
# How does the schema know that the primary key should not be provided on input?  

  
inventory_schema = InventorySchema()
inventory_many_schema = InventorySchema(many=True)