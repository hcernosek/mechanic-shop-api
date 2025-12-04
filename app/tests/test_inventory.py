from app.tests.test_base import APITestCase


class TestInventory(APITestCase):
    def test_create_inventory_success(self):
        payload = {"name": "Oil Filter", "price": 12.99}

        # POST should create an inventory item
        response = self.client.post("/inventory/", json=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "Oil Filter")
        self.assertEqual(response.json["price"], 12.99)

    def test_create_inventory_duplicate_name_returns_400(self):
        self.create_inventory(name="Spark Plug")  # create duplicate name
        payload = {"name": "Spark Plug", "price": 5.50}

        # Duplicate name should return 400 with error message
        response = self.client.post("/inventory/", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_get_all_inventory_returns_items(self):
        self.create_inventory(name="Brake Fluid", price=9.99)
        self.create_inventory(name="Alternator", price=199.99)

        # GET should return list of all inventory items
        response = self.client.get("/inventory/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_get_inventory_not_found_returns_404(self):
        # Requesting missing id returns 404
        response = self.client.get("/inventory/999")

        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json)

    def test_update_inventory_success(self):
        inventory = self.create_inventory(name="Air Filter", price=14.99)
        payload = {"name": "Air Filter", "price": 19.99}

        # PUT should update price
        response = self.client.put(f"/inventory/{inventory.id}", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["price"], 19.99)

    def test_update_inventory_invalid_payload_returns_400(self):
        inventory = self.create_inventory(name="Timing Belt", price=89.99)
        payload = {"name": "Timing Belt", "price": "invalid"}

        # Invalid price type should fail validation
        response = self.client.put(f"/inventory/{inventory.id}", json=payload)

        self.assertEqual(response.status_code, 400)

    def test_update_inventory_not_found_returns_404(self):
        payload = {"name": "Nonexistent", "price": 10.00}

        # Updating missing record should 404
        response = self.client.put("/inventory/999", json=payload)

        self.assertEqual(response.status_code, 404)

    def test_delete_inventory_success(self):
        inventory = self.create_inventory(name="Washer Fluid", price=3.99)

        # DELETE should remove the inventory item
        response = self.client.delete(f"/inventory/{inventory.id}")

        self.assertEqual(response.status_code, 200)

    def test_delete_inventory_not_found_returns_404(self):
        # Deleting a missing item returns 404
        response = self.client.delete("/inventory/999")

        self.assertEqual(response.status_code, 404)
