# src/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'Books'
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    isbn = db.Column(db.String(13), unique=True)
    genre = db.Column(db.String(50))
    publisher = db.Column(db.String(100))
    year_published = db.Column(db.Integer)
    price = db.Column(db.Float)
    quantity_in_stock = db.Column(db.Integer)

class Inventory(db.Model):
    __tablename__ = 'Inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('Books.book_id'))
    location = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    book = db.relationship('Book', backref='inventory')