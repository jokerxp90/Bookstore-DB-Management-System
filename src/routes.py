# src/routes.py
from flask import Blueprint, request, jsonify
from models import db, Book, SupplierOrders, Orders, Sales  # Absolute import

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'book_id': book.book_id,
        'title': book.title,
        'author': book.author,
        'price': book.price,
        'quantity_in_stock': book.quantity_in_stock,
        'isbn': book.isbn
    } for book in books]), 200

@inventory_bp.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    book = Book(
        title=data['title'],
        author=data.get('author'),
        price=data.get('price'),
        quantity_in_stock=data.get('quantity_in_stock', 0),
        isbn=data.get('isbn')
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book added', 'book_id': book.book_id}), 201

@inventory_bp.route('/supplier-orders', methods=['POST'])
def order_from_supplier():
    data = request.get_json()
    book_id = data['book_id']
    book = Book.query.get_or_404(book_id)
    if book.quantity_in_stock < 5:
        order = SupplierOrders(book_id=book_id, quantity=data.get('quantity', 10))
        db.session.add(order)
        db.session.commit()
        return jsonify({'message': 'Order placed with supplier', 'order_id': order.order_id}), 201
    return jsonify({'message': 'Stock sufficient, no order needed'}), 200

@inventory_bp.route('/supplier-orders/<int:order_id>', methods=['GET'])
def get_supplier_order(order_id):
    order = SupplierOrders.query.get_or_404(order_id)
    return jsonify({
        'order_id': order.order_id,
        'book_id': order.book_id,
        'quantity': order.quantity,
        'order_date': order.order_date.isoformat()
    }), 200

@inventory_bp.route('/orders', methods=['POST'])
def place_order():
    data = request.get_json()
    book_id = data['book_id']
    quantity = data['quantity']
    book = Book.query.get_or_404(book_id)
    if book.quantity_in_stock < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    order = Orders(book_id=book_id, quantity=quantity)
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order placed', 'order_id': order.order_id}), 201

@inventory_bp.route('/orders', methods=['GET'])
def get_orders():
    orders = Orders.query.all()
    return jsonify([{
        'order_id': order.order_id,
        'book_id': order.book_id,
        'quantity': order.quantity,
        'status': order.status,
        'order_date': order.order_date.isoformat()
    } for order in orders]), 200

@inventory_bp.route('/orders/<int:order_id>/confirm', methods=['POST'])
def confirm_order(order_id):
    order = Orders.query.get_or_404(order_id)
    if order.status != 'Pending':
        return jsonify({'error': 'Order already processed'}), 400
    book = Book.query.get(order.book_id)
    book.quantity_in_stock -= order.quantity
    order.status = 'Confirmed'
    sale = Sales(
        book_id=book.book_id,
        quantity_sold=order.quantity,
        total_price=book.price * order.quantity
    )
    db.session.add(sale)
    db.session.commit()
    return jsonify({'message': 'Order confirmed', 'order_id': order.order_id}), 200

@inventory_bp.route('/sales/report', methods=['GET'])
def sales_report():
    start_date = request.args.get('start_date')
    sales = Sales.query
    if start_date:
        sales = sales.filter(Sales.sale_date >= start_date)
    sales = sales.all()
    total = sum(sale.total_price for sale in sales)
    return jsonify({
        'total_sales': total,
        'transactions': len(sales),
        'details': [{
            'sale_id': sale.sale_id,
            'book_id': sale.book_id,
            'quantity_sold': sale.quantity_sold,
            'total_price': sale.total_price,
            'sale_date': sale.sale_date.isoformat()
        } for sale in sales]
    }), 200