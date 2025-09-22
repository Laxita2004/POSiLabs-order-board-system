from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import threading
import time
import json
import os

app = Flask(__name__)

ORDERS_FILE = 'orders.json'
STALE_ORDER_LIFETIME_HOURS = 24
CLEANUP_INTERVAL_SECONDS = 300  # every 5 minutes

# Load and save helpers
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_orders():
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

orders = load_orders()
orders_lock = threading.Lock()

# to ensure orders.json conforms to new schema
for i, o in enumerate(orders):
    o.setdefault("phoneNumber", "")
    o.setdefault("storeLocation", "Default-Store")
    o.setdefault("orderType", "Takeaway")
    o.setdefault("status", 1)  # default to Prep
    o.setdefault("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

save_orders()

@app.route('/orderstatus', methods=['POST'])
def update_order_status():
    data = request.json

    # Normalize order number to string
    order_number = str(data["orderNumber"])
    phone_number = str(data.get("phoneNumber", ""))
    store_location = data.get("storeLocation", "Default-Store")
    order_type = data.get("orderType", "Takeaway")  # dine-in, takeaway, delivery
    status = int(data.get("status", 1))  # 1=Prep by default
    timestamp = data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if status not in [1, 2, 3]:
        status = 1
    
    order_obj = {
        "orderNumber": order_number,
        "phoneNumber": phone_number,
        "storeLocation": store_location,
        "orderType": order_type,
        "status": status,
        "timestamp": timestamp
    }

    with orders_lock:
        for existing in orders:
            if str(existing["orderNumber"]) == order_number:
                existing.update(order_obj)
                break
        else:
            orders.append(order_obj)
        save_orders()

    return jsonify({"success": True, "order": order_obj})

@app.route('/orders', methods=['GET'])
def get_orders():
    with orders_lock:
        return jsonify(orders)

@app.route('/orders/<order_number>', methods=['DELETE'])
def delete_order(order_number):
    global orders
    with orders_lock:
        orders = [o for o in orders if str(o['orderNumber']) != str(order_number)]
        save_orders()
    return jsonify({"deleted": order_number})

# Background cleanup
def cleanup_stale_orders():
    while True:
        time.sleep(CLEANUP_INTERVAL_SECONDS)
        now = datetime.now()
        stale_threshold = now - timedelta(hours=STALE_ORDER_LIFETIME_HOURS)

        with orders_lock:
            fresh_orders = []
            for order in orders:
                raw_time = order.get("timestamp")
                try:
                    order_time = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                except:
                    continue  # skip bad timestamps

                if order_time >= stale_threshold:
                    fresh_orders.append(order)
                else:
                    print(f"[STALE REMOVED] Order {order.get('orderNumber')} from {raw_time}")

            if len(fresh_orders) != len(orders):
                orders[:] = fresh_orders
                save_orders()

# Start background cleanup thread
threading.Thread(target=cleanup_stale_orders, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)