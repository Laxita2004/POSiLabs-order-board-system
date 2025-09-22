# DB structure
from database import db
from datetime import datetime

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    order_type = db.Column(db.String(50), default='Takeaway')  # dine-in, takeaway, delivery
    status = db.Column(db.Integer, default=1)  # 1=Prep, 2=Prepared, 3=Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "orderNumber": self.order_number,
            "phoneNumber": self.phone_number,
            "storeId": self.store_id,
            "orderType": self.order_type,
            "status": self.status,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updatedAt": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def from_dict(data):
        return Order(
            order_number=data.get("orderNumber"),
            phone_number=data.get("phoneNumber", ""),
            store_id=data.get("storeId"),
            order_type=data.get("orderType", "Takeaway"),
            status=int(data.get("status", 1))
        )
    
class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    orders = db.relationship('Order', backref='store', lazy=True)
    
class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    background_image = db.Column(db.String(200))
    logo_url = db.Column(db.String(200))