from app.models import Mechanic, db
from app.tests.test_base import APITestCase


class TestMechanic(APITestCase):
    def test_create_mechanic_success(self):
        payload = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "555-123-4567",
            "salary": 55000.0,
        }

        # POST to create a mechanic with valid data
        response = self.client.post("/mechanics/", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], payload["name"])
        self.assertEqual(response.json["email"], payload["email"])

    def test_create_mechanic_duplicate_email_returns_400(self):
        self.create_mechanic(email="dup@example.com")  # seed existing mechanic
        payload = {
            "name": "Duplicate",
            "email": "dup@example.com",
            "phone": "555-222-2222",
            "salary": 60000.0,
        }

        # Duplicate email should fail validation
        response = self.client.post("/mechanics/", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_get_mechanics_returns_list(self):
        self.create_mechanic(name="Mechanic One", email="one@example.com")
        self.create_mechanic(name="Mechanic Two", email="two@example.com")

        # GET should return both mechanics
        response = self.client.get("/mechanics/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_get_mechanic_not_found_returns_404(self):
        # Requesting an id that does not exist should 404
        response = self.client.get("/mechanics/999")

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

    def test_update_mechanic_success(self):
        mechanic = self.create_mechanic()
        payload = {
            "name": "Updated Name",
            "email": mechanic.email,
            "phone": mechanic.phone,
            "salary": 75000.0,
        }

        # PUT should update fields when payload is valid
        response = self.client.put(f"/mechanics/{mechanic.id}", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["name"], "Updated Name")
        self.assertEqual(response.json["salary"], 75000.0)
        self.assertEqual(response.json["email"], mechanic.email)
        self.assertEqual(response.json["phone"], mechanic.phone)

    def test_update_mechanic_invalid_payload_returns_400(self):
        mechanic = self.create_mechanic()
        payload = {
            "name": "Bad Payload",
            "email": mechanic.email,
            "phone": "555-000-0000",
            # salary missing to trigger validation error
        }

        # Missing required salary should return validation error
        response = self.client.put(f"/mechanics/{mechanic.id}", json=payload)

        self.assertEqual(response.status_code, 400)

    def test_update_mechanic_not_found_returns_404(self):
        payload = {
            "name": "Nope",
            "email": "missing@example.com",
            "phone": "555-444-4444",
            "salary": 60000.0,
        }

        # Updating a missing mechanic should 404
        response = self.client.put("/mechanics/999", json=payload)

        self.assertEqual(response.status_code, 404)

    def test_delete_mechanic_success(self):
        mechanic = self.create_mechanic()

        # DELETE should remove the mechanic
        response = self.client.delete(f"/mechanics/{mechanic.id}")

        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            db_mechanic = db.session.get(Mechanic, mechanic.id)
            self.assertIsNone(db_mechanic)

    def test_delete_mechanic_not_found_returns_404(self):
        # Deleting non-existent mechanic should 404
        response = self.client.delete("/mechanics/999")

        self.assertEqual(response.status_code, 404)

    def test_get_top_mechanics_orders_by_ticket_count(self):
        customer = self.create_customer()
        mechanic_many = self.create_mechanic(name="Busy Mech", email="busy@example.com")
        mechanic_few = self.create_mechanic(name="Free Mech", email="free@example.com")
        self.create_service_ticket(
            customer=customer, mechanics=[mechanic_many], vin="1HGCM82633A000001"
        )
        self.create_service_ticket(
            customer=customer, mechanics=[mechanic_many], vin="1HGCM82633A000002"
        )
        self.create_service_ticket(
            customer=customer, mechanics=[mechanic_few], vin="1HGCM82633A000003"
        )

        # Top mechanics should be ordered by descending ticket count
        response = self.client.get("/mechanics/top_mechanics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]["name"], "Busy Mech")
