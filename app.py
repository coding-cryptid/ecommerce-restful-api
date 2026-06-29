import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.exceptions import BadRequest, NotFound

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    orders = relationship('Order', backref='user', cascade='all, delete-orphan')

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primarykey=True, autoincrement=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primarykey=True, autoincrement=True)
    order_date = db.Column(DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    products = relationship('Product', secondary='order_product', backref='orders')

class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    order_id = db.Column(db.Integer, ForeignKey('order.id'), primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey('product.id'), primary_key=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)