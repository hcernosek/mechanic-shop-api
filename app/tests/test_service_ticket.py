from app.models import ServiceTicket, db
from app.tests.base_test import APITestCase


class TestServiceTicket(APITestCase):
    def test_create_service_ticket_success(self):
        customer = self.create_customer()
        mechanic = self.create_mechanic()
        inventory = self.create_inventory()
        payload = {
            "vin": "1HGCM82633A765432",
            "service_date": "2024-02-01",
            "service_desc": "Brake service",
            "customer_id": customer.id,
            "mechanic_ids": [mechanic.id],
            "inventory": [{"inventory_id": inventory.id, "quantity": 2}],
        }

        # POST should create ticket, attach mechanic and inventory quantities
        response = self.client.post("/service_tickets/", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["service_ticket"]["vin"], payload["vin"])
        self.assertEqual(len(response.json["service_ticket"]["mechanics"]), 1)
        self.assertEqual(
            response.json["service_ticket"]["service_inventory"][0]["quantity"], 2
        )

    def test_create_service_ticket_invalid_inventory_returns_400(self):
        customer = self.create_customer()
        payload = {
            "vin": "1HGCM82633A123400",
            "service_date": "2024-03-01",
            "service_desc": "Alignment",
            "customer_id": customer.id,
            "inventory": [{"inventory_id": 999, "quantity": 1}],
        }

        # Invalid inventory id should roll back and return 400
        response = self.client.post("/service_tickets/", json=payload)

        self.assertEqual(response.status_code, 400)
        with self.app.app_context():
            tickets = db.session.query(ServiceTicket).all()
            self.assertEqual(len(tickets), 0)

    def test_get_all_service_tickets_returns_list(self):
        customer = self.create_customer()
        self.create_service_ticket(
            customer=customer, vin="1HGCM82633A000010", service_desc="Oil change"
        )
        self.create_service_ticket(
            customer=customer, vin="1HGCM82633A000011", service_desc="Tire rotation"
        )

        # GET returns list of tickets
        response = self.client.get("/service_tickets/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_get_service_ticket_success(self):
        ticket = self.create_service_ticket(vin="1HGCM82633A000012")

        # GET specific id should return ticket
        response = self.client.get(f"/service_tickets/{ticket.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["vin"], "1HGCM82633A000012")

    def test_get_service_ticket_not_found_returns_404(self):
        # Missing id returns 404
        response = self.client.get("/service_tickets/999")

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

    def test_delete_service_ticket_success(self):
        ticket = self.create_service_ticket(vin="1HGCM82633A000013")

        # DELETE should remove ticket
        response = self.client.delete(f"/service_tickets/{ticket.id}")

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            deleted = db.session.get(ServiceTicket, ticket.id)
            self.assertIsNone(deleted)

    def test_delete_service_ticket_not_found_returns_404(self):
        # Deleting missing ticket returns 404
        response = self.client.delete("/service_tickets/999")

        self.assertEqual(response.status_code, 404)

    def test_assign_mechanics_to_ticket(self):
        ticket = self.create_service_ticket()
        mech_one = self.create_mechanic(name="Assign One", email="assign1@example.com")
        mech_two = self.create_mechanic(name="Assign Two", email="assign2@example.com")
        payload = {"add_mechanics_ids": [mech_one.id, mech_two.id]}

        # PUT should attach new mechanics to the ticket
        response = self.client.put(
            f"/service_tickets/{ticket.id}/assign_mechanics", json=payload
        )

        self.assertEqual(response.status_code, 200)
        mechanic_ids = [m["id"] for m in response.json["mechanics"]]
        self.assertCountEqual(mechanic_ids, [mech_one.id, mech_two.id])

    def test_assign_mechanics_ticket_not_found_returns_404(self):
        payload = {"add_mechanics_ids": [1, 2]}

        # Assigning to missing ticket returns 404
        response = self.client.put("/service_tickets/999/assign_mechanics", json=payload)

        self.assertEqual(response.status_code, 404)

    def test_remove_mechanics_from_ticket(self):
        mechanic_one = self.create_mechanic(name="Remove One", email="remove1@example.com")
        mechanic_two = self.create_mechanic(name="Remove Two", email="remove2@example.com")
        ticket = self.create_service_ticket(mechanics=[mechanic_one, mechanic_two])
        payload = {"remove_mechanics_ids": [mechanic_one.id]}

        # PUT should remove the specified mechanic from the ticket
        response = self.client.put(
            f"/service_tickets/{ticket.id}/remove_mechanics", json=payload
        )

        self.assertEqual(response.status_code, 200)
        mechanic_ids = [m["id"] for m in response.json["mechanics"]]
        self.assertEqual(mechanic_ids, [mechanic_two.id])

    def test_remove_mechanics_ticket_not_found_returns_404(self):
        payload = {"remove_mechanics_ids": [1]}

        # Removing mechanics from missing ticket returns 404
        response = self.client.put("/service_tickets/999/remove_mechanics", json=payload)

        self.assertEqual(response.status_code, 404)
