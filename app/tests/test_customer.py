from datetime import date

from app.models import Customer, ServiceTicket, db
from app.tests.test_base import APITestCase
from app.utils.util import encode_token


# Run Tests in terminal with: 
# ------------------------------
# python -m unittest discover tests
# python -m unittest discover -s app/tests
# python -m unittest discover -s app/tests -p "test_*.py"
# python -m unittest discover -s app/tests -p "test_customer.py"


class TestCustomer(APITestCase):
    def setUp(self):
        super().setUp()
        # seed three customers we can query/update
        db.session.add_all(
            [
                Customer(
                    name="test_customerA",
                    email="testa@email.com",
                    phone="123 456 7890",
                    password="testA123",
                ),
                Customer(
                    name="test_customerB",
                    email="testb@email.com",
                    phone="234 567 8901",
                    password="testB123",
                ),
                Customer(
                    name="test_customerC",
                    email="testc@email.com",
                    phone="345 678 9012",
                    password="testC123",
                ),
            ]
        )
        db.session.commit()
        self.token = encode_token(1)  # token helper used in deletion tests

    def _auth_headers(self, customer_id=1):
        # helper to build Authorization header with a JWT for a given customer id
        return {"Authorization": f"Bearer {encode_token(customer_id)}"}

    def test_create_customer(self):
        customer_payload = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password": "s3cretPass",
            "phone": "555-123-4567"
            }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Jane Doe")
        self.assertEqual(response.json['email'], "jane.doe@example.com")


    def test_invalid_creation(self):
        # missing email should fail validation
        customer_payload = {
            "name": "Jane Doe",
            "password": "s3cretPass",
            "phone": "555-123-4567"
            }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json)
        self.assertIn('Missing data for required field.', response.json['email'])


    def test_duplicate_email_creation(self):
        # reusing an existing email should be rejected
        customer_payload = {
            "name": "Another User",
            "email": "testa@email.com",
            "password": "anotherPass",
            "phone": "999-999-9999"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['error'], "Email already associated with a customer.")
    

    def test_login_customer(self):
        # valid credentials return a token
        credentials = {
            "email": "testa@email.com",
            "password": "testA123"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(response.json['message'], 'Login successful.')


    def test_invalid_login(self):
        # bad credentials should be unauthorized
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid email or password.')


    def test_get_customers(self):
        # list returns all seeded customers
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)


    def test_get_customer_by_id(self):
        # found vs not found lookup
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'test_customerA')

        not_found = self.client.get('/customers/999')
        self.assertEqual(not_found.status_code, 404)
        self.assertEqual(not_found.json['error'], 'Customer not found.')


    def test_update_customer(self):
        # update existing customer and confirm fields
        update_payload = {
            "name": "Updated CustomerA",
            "phone": "555-111-2222",
            "email": "updatedA@email.com",
            "password": "newPass123"
        }

        response = self.client.put('/customers/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], update_payload['name'])
        self.assertEqual(response.json['email'], update_payload['email'])
        self.assertEqual(response.json['phone'], update_payload['phone'])

    def test_update_customer_validation_error(self):
        # missing required email should fail validation
        update_payload = {
            "name": "No Email User",
            "phone": "555-111-2222",
            "password": "newPass123"
        }

        response = self.client.put('/customers/1', json=update_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json)


    def test_delete_customer(self):
        # delete with valid auth removes customer
        response = self.client.delete('/customers/', headers=self._auth_headers(1))
        self.assertEqual(response.status_code, 200)
        follow_up = self.client.get('/customers/1')
        self.assertEqual(follow_up.status_code, 404)


    def test_delete_customer_not_found(self):
        # deleting with a token for missing customer should 404
        response = self.client.delete('/customers/', headers=self._auth_headers(999))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Customer not found.')


    def test_get_my_tickets(self):
        # create a ticket for customer 1 and ensure it is returned with auth
        ticket = ServiceTicket(
            vin="1HGCM82633A004352",
            service_date=date.today(),
            service_desc="Oil change",
            customer_id=1,
        )
        db.session.add(ticket)
        db.session.commit()

        response = self.client.get('/customers/my-tickets', headers=self._auth_headers(1))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['vin'], "1HGCM82633A004352")


    def test_get_my_tickets_requires_auth(self):
        # missing Authorization header should block access
        response = self.client.get('/customers/my-tickets')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Login to access this resource')
