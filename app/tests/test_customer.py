from app import create_app
from app.models import db, Customer
from datetime import datetime
from app.utils.util import encode_token
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(
            name="test_user", 
            email="test@email.com", 
            phone="123 456 7890", 
            password="test"
            )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

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


    def test_invalid_creation(self):
        customer_payload = {
            "name": "Jane Doe",
            "password": "s3cretPass",
            "phone": "555-123-4567"
            }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])
    

    def test_login_customer(self):
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'Login successful.')
        return response.json['token']


    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid email or password!')


    def test_update_member(self):
        update_payload = {
            "name": "Peter",
            "phone": "",
            "email": "",
            "password": ""
        }

        headers = {'Authorization': "Bearer " + self.test_login_customer()}

        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter') 
        self.assertEqual(response.json['email'], 'test@email.com')

# POST /customers/login

# request: 
# {
#   "email": "jane.doe@example.com",
#   "password": "s3cretPass"
# }

# response:
# {
#   "status": "success",
#   "message": "Login successful.",
#   "token": "<jwt-token-string>"
# }

# POST /customers

# request:
# {
#   "name": "Jane Doe",
#   "email": "jane.doe@example.com",
#   "password": "s3cretPass",
#   "phone": "555-123-4567"
# }
# response:
# {
#   "id": 1,
#   "name": "Jane Doe",
#   "email": "jane.doe@example.com",
#   "phone": "555-123-4567"
# }

# GET /customers/

# [
#   {
#     "id": 1,
#     "name": "Jane Doe",
#     "email": "jane.doe@example.com",
#     "phone": "555-123-4567"
#   },
#   {
#     "id": 2,
#     "name": "Bob Smith",
#     "email": "bob@example.com",
#     "phone": "555-999-0000"
#   }
# ]

# GET /customers/{id}

# response:
# {
#   "id": 1,
#   "name": "Jane Doe",
#   "email": "jane.doe@example.com",
#   "phone": "555-123-4567"
# }

# PUT /customers/{id}

# request:
# {
#   "name": "Jane A. Doe",
#   "email": "jane.doe@example.com",
#   "password": "newSecret",
#   "phone": "555-000-1111"
# }

# response:
# {
#   "id": 1,
#   "name": "Jane A. Doe",
#   "email": "jane.doe@example.com",
#   "phone": "555-000-1111"
# }

# DELETE /customers/{id} (protected)

# {
#   "message": "Customer id: 1, successfully deleted."
# }