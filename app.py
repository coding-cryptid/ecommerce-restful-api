import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, validate, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
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

# ===== MODELS/TABLES =====
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True, nullable=False)
    orders = relationship('Order', backref='user', cascade='all, delete-orphan')

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    products = relationship('Product', secondary='order_product', backref='orders')

class OrderProduct(db.Model):
    __tablename__ = 'order_product'
    order_id = db.Column(db.Integer, ForeignKey('order.id'), primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey('product.id'), primary_key=True)

    __table_args__ = (
        UniqueConstraint('order_id', 'product_id', name='unique_order_product'),
    )

# ===== SCHEMAS =====
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
    
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    address = fields.String(allow_none=True)


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True
    
    product_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Float(required=True, validate=validate.Range(min=0))


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
        include_fk = True
    
    order_date = fields.DateTime(required=True)
    user_id = fields.Integer(required=True)
    products = fields.Nested(ProductSchema, many=True)

# ===== ENDPOINTS =====
# ===== USER ENDPOINTS =====
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    schema = UserSchema(many=True)
    return jsonify(schema.dump(users)), 200

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    schema = UserSchema()
    return jsonify(schema.dump(user)), 200

@app.route('/users', methods=['POST'])
def create_user():
    schema = UserSchema()
    try:
        user = schema.load(request.json)
        db.session.add(user)
        db.session.commit()
        return jsonify(schema.dump(user)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    schema = UserSchema()
    try:
        updated_user = schema.load(request.json, instance=user, partial=True)
        db.session.commit()
        return jsonify(schema.dump(updated_user)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


# ===== PRODUCT ENDPOINTS =====
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    schema = ProductSchema(many=True)
    return jsonify(schema.dump(products)), 200

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    schema = ProductSchema()
    return jsonify(schema.dump(product)), 200

@app.route('/products', methods=['POST'])
def create_product():
    schema = ProductSchema()
    try:
        product = schema.load(request.json)
        db.session.add(product)
        db.session.commit()
        return jsonify(schema.dump(product)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    schema = ProductSchema()
    try:
        updated_product = schema.load(request.json, instance=product, partial=True)
        db.session.commit()
        return jsonify(schema.dump(updated_product)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200


# ===== ORDER ENDPOINTS =====
@app.route('/orders', methods=['POST'])
def create_order():
    schema = OrderSchema()
    try:
        order = schema.load(request.json)
        db.session.add(order)
        db.session.commit()
        return jsonify(schema.dump(order)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    order = Order.query.get(order_id)
    product = Product.query.get(product_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product in order.products:
        return jsonify({'error': 'Product already in order'}), 400
    
    order.products.append(product)
    db.session.commit()
    
    schema = OrderSchema()
    return jsonify(schema.dump(order)), 200

@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    order = Order.query.get(order_id)
    product = Product.query.get(product_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if product not in order.products:
        return jsonify({'error': 'Product not in order'}), 404
    
    order.products.remove(product)
    db.session.commit()
    
    schema = OrderSchema()
    return jsonify(schema.dump(order)), 200

@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    orders = Order.query.filter_by(user_id=user_id).all()
    schema = OrderSchema(many=True)
    return jsonify(schema.dump(orders)), 200

@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_order_products(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    products = order.products
    schema = ProductSchema(many=True)
    return jsonify(schema.dump(products)), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
