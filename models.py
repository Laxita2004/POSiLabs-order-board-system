# DB structure
from database import db
from datetime import datetime

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20))
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    order_type = db.Column(db.String(50))
    status = db.Column(db.Integer)  # 1 = preparing, 3 = ready
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    orders = db.relationship('Order', backref='store', lazy=True)
    
class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    background_image = db.Column(db.String(200))
    logo_url = db.Column(db.String(200))