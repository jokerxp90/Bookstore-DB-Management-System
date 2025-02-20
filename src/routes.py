# src/routes.py
from flask import Blueprint, request, jsonify
from models import Book, Inventory, db

inventory_bp = Blueprint('inventory', __name__)

# Task 1.1: Add new books
@inventory_bp.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    if not data.get('title') or not data.get('price'):
        return jsonify({'error': 'Title and price are required'}), 400
    
    new_book = Book(
        title=data['title'],
        author=data.get('author'),
        isbn=data.get('isbn'),
        genre=data.get('genre'),
        publisher=data.get('publisher'),
        year_published=data.get('year_published'),
        price=data.get('price'),
        quantity_in_stock=max(data.get('quantity_in_stock', 0), 0)  # No negative stock
    )
    db.session.add(new_book)
    db.session.commit()

    new_inventory = Inventory(book_id=new_book.book_id, location=data.get('location', 'Main Shelf'))
    db.session.add(new_inventory)
    db.session.commit()

    return jsonify({'message': 'Book added', 'book_id': new_book.book_id}), 201

# Task 1.2: Update inventory on sales + Real-time updates
@inventory_bp.route('/books/<int:book_id>/sell', methods=['POST'])
def sell_book(book_id):
    data = request.get_json()
    quantity_sold = max(data.get('quantity', 1), 1)  # At least 1
    book = Book.query.get_or_404(book_id)

    if book.quantity_in_stock < quantity_sold:
        return jsonify({'error': 'Not enough stock'}), 400

    book.quantity_in_stock -= quantity_sold
    inventory = Inventory.query.filter_by(book_id=book_id).first()
    if inventory:
        inventory.last_updated = db.func.current_timestamp()
    db.session.commit()

    # Task 2.1: Mock sales record
    sale = {
        'book_id': book_id,
        'title': book.title,
        'quantity_sold': quantity_sold,
        'total_price': float(book.price) * quantity_sold,
        'timestamp': inventory.last_updated.isoformat() if inventory else db.func.current_timestamp().isoformat()
    }
    return jsonify({'message': 'Sale recorded', 'sale': sale}), 200

# Helper: List books
@inventory_bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'book_id': b.book_id,
        'title': b.title,
        'author': b.author,
        'genre': b.genre,
        'quantity_in_stock': b.quantity_in_stock,
        'last_updated': b.inventory[0].last_updated.isoformat() if b.inventory else 'N/A'
    } for b in books]), 200