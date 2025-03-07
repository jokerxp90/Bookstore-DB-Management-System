# tests/test_sprint2.py
import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_bookstore.db'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

# Task 2.1, 2.2: Enhanced Sales
def test_sales_and_report(client):
    client.post('/inventory/books', json={'title': 'Sale Book', 'price': 10.00, 'quantity_in_stock': 10, 'isbn': '1111111111111'})
    response = client.post('/inventory/books/1/sell', json={'quantity': 2})
    assert response.status_code == 200
    assert response.get_json()['sale_id'] == 1
    report = client.get('/inventory/sales/report').get_json()
    assert report['total_sales'] == 20.00
    assert report['transactions'] == 1

# Task 3.1, 3.2: Supplier Orders
def test_supplier_order(client):
    client.post('/inventory/books', json={'title': 'Low Stock', 'price': 5.00, 'quantity_in_stock': 3, 'isbn': '2222222222222'})
    response = client.post('/inventory/supplier-orders', json={'book_id': 1, 'quantity': 10})
    assert response.status_code == 201
    assert response.get_json()['order_id'] == 1
    status = client.get('/inventory/supplier-orders/1').get_json()
    assert status['status'] == 'Pending'

# Task 4.1: Browse Inventory
def test_get_books(client):
    client.post('/inventory/books', json={'title': 'Fantasy Book', 'price': 15.00, 'quantity_in_stock': 5, 'genre': 'Fantasy', 'isbn': '3333333333333'})
    response = client.get('/inventory/books?genre=Fantasy').get_json()
    assert len(response) == 1
    assert response[0]['title'] == 'Fantasy Book'

# Task 4.2, 4.3: Customer Orders
def test_customer_order(client):
    client.post('/inventory/books', json={'title': 'Order Book', 'price': 20.00, 'quantity_in_stock': 10, 'isbn': '4444444444444'})
    response = client.post('/inventory/orders', json={'book_id': 1, 'quantity': 3})
    assert response.status_code == 201
    confirm = client.post('/inventory/orders/1/confirm', json={})
    assert confirm.status_code == 200
    books = client.get('/inventory/books').get_json()
    assert books[0]['quantity_in_stock'] == 7