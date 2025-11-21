# Coding Temple Application Factory Pattern Assignment Submission

## Project Routes

### Customers:

- Basic CRUD Routes:
    - `POST /customers/` -> create customers
    - `GET /customers/` -> get all customers
    - `GET /customers/{id}` -> get single customer by id
    - `PUT /customers/{id}` -> update
    - `DELETE /customers/` -> delete (requires token for customer)
- Login Route `POST /customers/login`
  - customer login that return token. token used to access delete and customer service tickets route
- Customer Tickets Route  `GET /customers/my-tickets`
  - access customer tickets with token authentication

### Mechanics

- Basic CRUD Routes:
    - `POST /mechanics/` -> create new mechanic
    - `GET /mechanics/{id}` -> get a single(with id) or all mechanics
    - `PUT /inventory/{id}` -> update a mechanic
    - `DELETE /inventory/{id}` -> delete a mechanic
- `GET /mechanics/top_mechanics` -> get mechanics sorted by top performers

### Inventory

- Basic CRUD Routes:
    - `POST /inventory/` -> create part
    - `GET /inventory/` -> list parts
    - `PUT /inventory/{id}` -> update
    - `DELETE /inventory/{id}` -> delete

### Service Tickets

  - `POST /service_tickets/` -> create a ticket. 
  - `GET /service_tickets/` -> list tickets
  - `GET /service_tickets/{id}` -> get single ticket
  - `PUT /service_tickets//{id}/remove_mechanics` -> remove mechanics from an existing service ticket
  - `PUT /service_tickets//{id}/assign_mechanics` -> add mechanics to an existing service ticket
  - `DELETE /service_tickets/{id}` -> delete
