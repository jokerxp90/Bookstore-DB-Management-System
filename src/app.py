# src/app.py
from flask import Flask
from models import db
from routes import inventory_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.register_blueprint(inventory_bp, url_prefix='/inventory')

@app.route('/')
def home():
    return 'Welcome to the Bookstore Management System API'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)