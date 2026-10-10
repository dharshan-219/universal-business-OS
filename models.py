from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(db.String(255), nullable=False)

    businesses = db.relationship(
        "Business",
        backref="owner",
        lazy=True
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    business_type = db.Column(db.String(100), nullable=False)

    country = db.Column(db.String(100), nullable=False)

    currency = db.Column(db.String(20), nullable=False)

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    phone = db.Column(db.String(30), nullable=True)

    email = db.Column(db.String(120), nullable=True)

    address = db.Column(db.Text, nullable=True)

    notes = db.Column(db.Text, nullable=True)

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    sku = db.Column(db.String(100), nullable=True)

    category = db.Column(db.String(100), nullable=True)

    selling_price = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    purchase_price = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    stock_quantity = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    unit = db.Column(
        db.String(50),
        nullable=False,
        default="piece"
    )

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(db.Float, nullable=False)

    unit_price = db.Column(db.Float, nullable=False)

    total_amount = db.Column(db.Float, nullable=False)

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=True,
        default=datetime.utcnow
    )

    customer = db.relationship(
        "Customer",
        backref="sales"
    )

    product = db.relationship(
        "Product",
        backref="sales"
    )


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    phone = db.Column(db.String(30), nullable=True)

    email = db.Column(db.String(120), nullable=True)

    address = db.Column(db.Text, nullable=True)

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("supplier.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(db.Float, nullable=False)

    unit_cost = db.Column(db.Float, nullable=False)

    total_amount = db.Column(db.Float, nullable=False)

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    supplier = db.relationship("Supplier")

    product = db.relationship("Product")


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)

    category = db.Column(db.String(100), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    description = db.Column(db.Text, nullable=True)

    expense_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=True
    )

    phone = db.Column(
        db.String(30),
        nullable=True
    )

    job_title = db.Column(
        db.String(100),
        nullable=False
    )

    salary = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    hire_date = db.Column(
        db.Date,
        nullable=True,
        default=date.today
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Active"
    )

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    budget = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    deadline = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Planned"
    )

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    subject = db.Column(
        db.String(200),
        nullable=False
    )

    customer_name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Medium"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Open"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    business_id = db.Column(
        db.Integer,
        db.ForeignKey("business.id"),
        nullable=False
    )
