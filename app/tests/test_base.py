import unittest
from datetime import date

from app import create_app
from app.models import (
    Customer,
    Inventory,
    Mechanic,
    ServiceInventory,
    ServiceTicket,
    db,
)

# Set up for base test case with common utilities for all API test classes 
# e.g. TestMechanic, TestCustomer, TestServiceTicket
# Receives utility via inheritance by other test classes

class APITestCase(unittest.TestCase):

    # Before each test: Return a new Flask app instance, configured for testing
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.app.config["TESTING"] = True
        self.app_context = self.app.app_context() # build application context object for testing app
        self.app_context.push()  # enter app context so db/session are available
        db.drop_all()  # start with a clean schema each test run
        db.create_all()  # recreate tables in the in-memory SQLite db
        self.client = self.app.test_client()

    # After each test: Remove session (close), drop all tables, exit app context
    def tearDown(self):
        db.session.remove() 
        db.drop_all() 
        self.app_context.pop()

    def create_customer(self, name="Jane Customer", email="jane@example.com"):
        customer = Customer(
            name=name,
            email=email,
            password="secret",
            phone="555-000-0000",
        )
        db.session.add(customer) 
        db.session.commit()
        return customer

    def create_mechanic(
        self,
        name="Mike Mechanic",
        email="mike@example.com",
        phone="555-111-1111",
        salary=60000.0,
    ):
        mechanic = Mechanic(name=name, email=email, phone=phone, salary=salary)
        db.session.add(mechanic)
        db.session.commit()
        return mechanic

    def create_inventory(self, name="Brake Pads", price=49.99):
        inventory = Inventory(name=name, price=price)
        db.session.add(inventory)
        db.session.commit()
        return inventory

    def create_service_ticket(
        self,
        customer=None,
        vin="1HGCM82633A123456",
        service_date=date(2024, 1, 1),
        service_desc="Oil change",
        mechanics=None,
        inventory_items=None,
    ):
        if not customer:
            customer = self.create_customer()  # ensure a customer exists

        ticket = ServiceTicket(
            vin=vin,
            service_date=service_date,
            service_desc=service_desc,
            customer_id=customer.id,
        )
        db.session.add(ticket)
        db.session.flush()  # flush to get ticket.id without full commit

        if mechanics:
            ticket.mechanics.extend(mechanics)  # many-to-many relation

        if inventory_items:
            for inventory, quantity in inventory_items:
                service_inventory = ServiceInventory(
                    ticket_id=ticket.id,
                    inventory_id=inventory.id,
                    quantity=quantity,
                )
                db.session.add(service_inventory)

        db.session.commit()  # final commit
        return ticket
