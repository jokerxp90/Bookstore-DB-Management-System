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

def test_enhanced_sales(client):
    client.post('/inventory/books', json={'title': 'Book1', 'price': 10.00, 'quantity_in_stock': 10})
    response = client.post('/inventory/books/1/sell', json={'quantity': 2})
    assert response.status_code == 200
    assert response.get_json()['sale_id'] == 1
    report = client.get('/inventory/sales/report').get_json()
    assert report['total_sales'] == 20.00
    assert report['transactions'] == 1

def test_supplier_order(client):
    client.post('/inventory/books', json={'title': 'Book2', 'price': 5.00, 'quantity_in_stock': 3})
    response = client.post('/inventory/supplier-orders', json={'book_id': 1, 'quantity': 10})
    assert response.status_code == 201
    status = client.get('/inventory/supplier-orders/1').get_json()
    assert status['status'] == 'Pending'

def test_customer_order(client):
    client.post('/inventory/books', json={'title': 'Book3', 'price': 15.00, 'quantity_in_stock': 5})
    response = client.post('/inventory/orders', json={'book_id': 1, 'quantity': 2})
    assert response.status_code == 201
    confirm = client.post('/inventory/orders/1/confirm')
    assert confirm.status_code == 200
    books = client.get('/inventory/books').get_json()
    assert books[0]['quantity_in_stock'] == 3