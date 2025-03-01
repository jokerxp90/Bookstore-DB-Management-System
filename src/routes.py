# src/routes.py
from flask import Blueprint, request, jsonify
from models import Book, Inventory, Sales, SupplierOrders, Orders, db

inventory_bp = Blueprint('inventory', __name__)

# Task 1.1 (Sprint 1): Add new books
@inventory_bp.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    if not data.get('title') or not data.get('price'):
        return jsonify({'error': 'Title and price are required'}), 400
    isbn = data.get('isbn')
    if isbn and Book.query.filter_by(isbn=isbn).first():
        return jsonify({'error': 'ISBN already exists'}), 400
    new_book = Book(
        title=data['title'],
        author=data.get('author'),
        isbn=data.get('isbn'),
        genre=data.get('genre'),
        publisher=data.get('publisher'),
        year_published=data.get('year_published'),
        price=data.get('price'),
        quantity_in_stock=max(data.get('quantity_in_stock', 0), 0)
    )
    db.session.add(new_book)
    db.session.commit()
    new_inventory = Inventory(book_id=new_book.book_id, location=data.get('location', 'Main Shelf'))
    db.session.add(new_inventory)
    db.session.commit()
    return jsonify({'message': 'Book added', 'book_id': new_book.book_id}), 201

# Task 4.1 Enhanced inventory browsing with filters
@inventory_bp.route('/books', methods=['GET'])
def get_books():
    genre = request.args.get('genre')
    books = Book.query
    if genre:
        books = books.filter_by(genre=genre)
    books = books.all()
    return jsonify([{
        'book_id': b.book_id,
        'title': b.title,
        'author': b.author,
        'genre': b.genre,
        'quantity_in_stock': b.quantity_in_stock,
        'last_updated': b.inventory[0].last_updated.isoformat() if b.inventory else None  # Safely handle empty inventory
    } for b in books]), 200

# Task 1.2 + 2.1: Update inventory and record sales
@inventory_bp.route('/books/<int:book_id>/sell', methods=['POST'])
def sell_book(book_id):
    data = request.get_json()
    quantity_sold = max(data.get('quantity', 1), 1)
    book = Book.query.get_or_404(book_id)
    if book.quantity_in_stock < quantity_sold:
        return jsonify({'error': 'Not enough stock'}), 400
    book.quantity_in_stock -= quantity_sold
    inventory = Inventory.query.filter_by(book_id=book_id).first()
    if inventory:
        inventory.last_updated = db.func.current_timestamp()
    sale = Sales(book_id=book_id, quantity_sold=quantity_sold, total_price=float(book.price) * quantity_sold)
    db.session.add(sale)
    db.session.commit()
    return jsonify({'message': 'Sale recorded', 'sale_id': sale.sale_id}), 200

# Task 2.2: Basic sales report
@inventory_bp.route('/sales/report', methods=['GET'])
def sales_report():
    sales = Sales.query.all()
    total = sum(sale.total_price for sale in sales)
    return jsonify({
        'total_sales': total,
        'transactions': len(sales),
        'details': [{'sale_id': s.sale_id, 'book_id': s.book_id, 'total_price': s.total_price} for s in sales]
    }), 200

# Task 3.1: Supplier order when stock low
@inventory_bp.route('/supplier-orders', methods=['POST'])
def order_from_supplier():
    data = request.get_json()
    book_id = data['book_id']
    book = Book.query.get_or_404(book_id)
    if book.quantity_in_stock < 5:  # Threshold for reorder
        order = SupplierOrders(book_id=book_id, quantity=data.get('quantity', 10))
        db.session.add(order)
        db.session.commit()
        return jsonify({'message': 'Order placed with supplier', 'order_id': order.order_id}), 201
    return jsonify({'message': 'Stock sufficient, no order needed'}), 200

# Task 3.2 : Track supplier order status
@inventory_bp.route('/supplier-orders/<int:order_id>', methods=['GET'])
def get_order_status(order_id):
    order = SupplierOrders.query.get_or_404(order_id)
    return jsonify({
        'order_id': order.order_id,
        'book_id': order.book_id,
        'quantity': order.quantity,
        'status': order.status,
        'order_date': order.order_date.isoformat()
    }), 200

# Task 4.2: Place customer order
@inventory_bp.route('/orders', methods=['POST'])
def place_customer_order():
    data = request.get_json()
    book_id = data['book_id']
    quantity = data.get('quantity', 1)
    book = Book.query.get_or_404(book_id)
    if book.quantity_in_stock < quantity:
        return jsonify({'error': 'Not enough stock'}), 400
    order = Orders(book_id=book_id, quantity=quantity)
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order placed', 'order_id': order.order_id}), 201

# Task 4.3 (Allan): Confirm order and update inventory
@inventory_bp.route('/orders/<int:order_id>/confirm', methods=['POST'])
def confirm_order(order_id):
    order = Orders.query.get_or_404(order_id)
    if order.status != 'Pending':
        return jsonify({'error': 'Order already processed'}), 400
    book = Book.query.get(order.book_id)
    book.quantity_in_stock -= order.quantity
    order.status = 'Confirmed'
    inventory = Inventory.query.filter_by(book_id=book.book_id).first()
    if inventory:
        inventory.last_updated = db.func.current_timestamp()
    db.session.commit()
    return jsonify({'message': 'Order confirmed', 'order_id': order.order_id}), 200