# tests/test_inventory.py
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

def test_add_book(client):
    response = client.post('/inventory/books', json={
        'title': 'Test Book',
        'price': 5.99,
        'quantity_in_stock': 10,
        'author': 'Test Author',
        'isbn': '1234567890123'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Book added'
    assert 'book_id' in data

def test_add_book_missing_title(client):
    response = client.post('/inventory/books', json={
        'price': 5.99
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_sell_book(client):
    response = client.post('/inventory/books', json={
        'title': 'Sell Book',
        'price': 10.00,
        'quantity_in_stock': 5
    })
    book_id = response.get_json()['book_id']
    response = client.post(f'/inventory/books/{book_id}/sell', json={'quantity': 2})
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Sale recorded'
    assert data['sale']['quantity_sold'] == 2
    assert data['sale']['total_price'] == 20.00

def test_sell_book_not_enough_stock(client):
    response = client.post('/inventory/books', json={
        'title': 'Low Stock Book',
        'price': 5.00,
        'quantity_in_stock': 1
    })
    book_id = response.get_json()['book_id']
    response = client.post(f'/inventory/books/{book_id}/sell', json={'quantity': 2})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_get_books(client):
    client.post('/inventory/books', json={
        'title': 'Get Book',
        'price': 7.99,
        'quantity_in_stock': 3
    })
    response = client.get('/inventory/books')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert any(book['title'] == 'Get Book' for book in data)