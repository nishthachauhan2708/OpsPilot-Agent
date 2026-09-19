import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import SessionLocal, engine, Base
from app.database.models import Customer, Product, Order, Inventory, Return, ActionRequest, AgentLog, CustomerIssue

def seed_database(db: Session):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # 1. Seed Products (15 items)
    products_data = [
        {"id": 1, "name": "AuraSound Wireless Noise-Canceling Headphones", "category": "Electronics", "price": 149.99},
        {"id": 2, "name": "VeloCity Ergonomic Mechanical Keyboard", "category": "Electronics", "price": 89.50},
        {"id": 3, "name": "Apex Precision Gaming Mouse", "category": "Electronics", "price": 49.99},
        {"id": 4, "name": "Lumina 27-inch 4K HDR Monitor", "category": "Electronics", "price": 329.00},
        {"id": 5, "name": "Nordic Craft Solid Oak Standing Desk", "category": "Furniture", "price": 499.00},
        {"id": 6, "name": "ErgoFlex Mesh Executive Chair", "category": "Furniture", "price": 219.00},
        {"id": 7, "name": "UrbanFit Smart Fitness Watch", "category": "Wearables", "price": 119.95},
        {"id": 8, "name": "PulseSound Portable Bluetooth Speaker", "category": "Electronics", "price": 59.99},
        {"id": 9, "name": "ThermalBrew Stainless Steel Smart Mug", "category": "Home & Kitchen", "price": 39.99},
        {"id": 10, "name": "EcoBreeze HEPA Air Purifier", "category": "Home & Kitchen", "price": 129.50},
        {"id": 11, "name": "ProGrip Leather Laptop Sleeve (15-inch)", "category": "Accessories", "price": 34.99},
        {"id": 12, "name": "UltraCharge 20,000mAh Power Bank", "category": "Electronics", "price": 44.99},
        {"id": 13, "name": "PureHydro Filtered Water Pitcher", "category": "Home & Kitchen", "price": 29.99},
        {"id": 14, "name": "FlexiStand Adjustable Tablet Arm", "category": "Accessories", "price": 24.99},
        {"id": 15, "name": "NovaGlow Ambient RGB Light Bar", "category": "Home & Kitchen", "price": 39.50},
    ]

    for p in products_data:
        if not db.query(Product).filter(Product.id == p["id"]).first():
            db.add(Product(**p))
    db.commit()

    # 2. Seed Inventory (15 records - matching products)
    inventory_data = [
        {"product_id": 1, "stock": 45, "reorder_level": 15},
        {"product_id": 2, "stock": 4, "reorder_level": 10},   # LOW STOCK
        {"product_id": 3, "stock": 25, "reorder_level": 10},
        {"product_id": 4, "stock": 3, "reorder_level": 5},    # LOW STOCK
        {"product_id": 5, "stock": 12, "reorder_level": 5},
        {"product_id": 6, "stock": 2, "reorder_level": 8},    # LOW STOCK
        {"product_id": 7, "stock": 50, "reorder_level": 15},
        {"product_id": 8, "stock": 8, "reorder_level": 10},   # LOW STOCK
        {"product_id": 9, "stock": 18, "reorder_level": 10},
        {"product_id": 10, "stock": 5, "reorder_level": 10},  # LOW STOCK
        {"product_id": 11, "stock": 60, "reorder_level": 20},
        {"product_id": 12, "stock": 14, "reorder_level": 15}, # LOW STOCK
        {"product_id": 13, "stock": 30, "reorder_level": 10},
        {"product_id": 14, "stock": 22, "reorder_level": 10},
        {"product_id": 15, "stock": 40, "reorder_level": 15},
    ]

    for i in inventory_data:
        if not db.query(Inventory).filter(Inventory.product_id == i["product_id"]).first():
            db.add(Inventory(**i))
    db.commit()

    # 3. Seed Customers (20 customers)
    customers_data = [
        {"id": 1, "name": "Aarav Sharma", "email": "aarav.sharma@example.com"},
        {"id": 2, "name": "Priya Patel", "email": "priya.patel@example.com"},
        {"id": 3, "name": "Rohan Mehta", "email": "rohan.mehta@example.com"},
        {"id": 4, "name": "Ananya Gupta", "email": "ananya.gupta@example.com"},
        {"id": 5, "name": "Vikram Singh", "email": "vikram.singh@example.com"},
        {"id": 6, "name": "Neha Joshi", "email": "neha.joshi@example.com"},
        {"id": 7, "name": "Siddharth Rao", "email": "siddharth.rao@example.com"},
        {"id": 8, "name": "Kavya Nair", "email": "kavya.nair@example.com"},
        {"id": 9, "name": "Aditya Verma", "email": "aditya.verma@example.com"},
        {"id": 10, "name": "Diya Sen", "email": "diya.sen@example.com"},
        {"id": 11, "name": "Rahul Kumar", "email": "rahul.kumar@example.com"},
        {"id": 12, "name": "Sneha Roy", "email": "sneha.roy@example.com"},
        {"id": 13, "name": "Karan Kapoor", "email": "karan.kapoor@example.com"},
        {"id": 14, "name": "Ishita Deshmukh", "email": "ishita.deshmukh@example.com"},
        {"id": 15, "name": "Manish Reddy", "email": "manish.reddy@example.com"},
        {"id": 16, "name": "Pooja Banerjee", "email": "pooja.banerjee@example.com"},
        {"id": 17, "name": "Tarun Bhatia", "email": "tarun.bhatia@example.com"},
        {"id": 18, "name": "Meera Iyer", "email": "meera.iyer@example.com"},
        {"id": 19, "name": "Varun Saxena", "email": "varun.saxena@example.com"},
        {"id": 20, "name": "Shreya Pandey", "email": "shreya.pandey@example.com"},
    ]

    now = datetime.datetime.utcnow()
    for c in customers_data:
        if not db.query(Customer).filter(Customer.id == c["id"]).first():
            db.add(Customer(id=c["id"], name=c["name"], email=c["email"], created_at=now - datetime.timedelta(days=30)))
    db.commit()

    # 4. Seed Orders (40 orders)
    orders_list = []
    
    # Explicit order 1042
    orders_list.append({
        "id": 1042,
        "customer_id": 1,
        "product_id": 1,
        "amount": 149.99,
        "order_date": now - datetime.timedelta(days=6),
        "expected_delivery": now - datetime.timedelta(days=2),
        "actual_delivery": None,
        "status": "delayed",
        "tracking_status": "In Transit - Delayed at Regional Sorting Hub (Customs inspection clearance pending)"
    })

    # Delayed orders (5 more)
    delayed_specs = [
        (1001, 2, 2, 89.50, 7, 2, "In Transit - Carrier vehicle malfunction delayed delivery"),
        (1005, 5, 4, 329.00, 8, 3, "In Transit - Weather disruption in transit zone"),
        (1012, 8, 6, 219.00, 5, 1, "In Transit - Address verification exception required"),
        (1020, 12, 8, 59.99, 6, 2, "In Transit - Missed hub transfer connection"),
        (1035, 18, 10, 129.50, 9, 4, "In Transit - Logistics depot backlog"),
    ]
    for oid, cid, pid, amt, past_ord, past_exp, track in delayed_specs:
        orders_list.append({
            "id": oid,
            "customer_id": cid,
            "product_id": pid,
            "amount": amt,
            "order_date": now - datetime.timedelta(days=past_ord),
            "expected_delivery": now - datetime.timedelta(days=past_exp),
            "actual_delivery": None,
            "status": "delayed",
            "tracking_status": track
        })

    # Shipped & Processing orders
    active_specs = [
        (1043, 3, 3, 49.99, 2, -2, "shipped", "In Transit - Out for final mile sorting"),
        (1044, 4, 5, 499.00, 1, -3, "processing", "Warehouse Picked - Packing in progress"),
        (1045, 6, 7, 119.95, 1, -2, "shipped", "In Transit - Handed over to Express Logistics"),
        (1046, 7, 9, 39.99, 2, -1, "shipped", "In Transit - Arrived at local distribution center"),
        (1047, 9, 11, 34.99, 1, -3, "processing", "Order Confirmed - Awaiting warehouse allocation"),
    ]
    for oid, cid, pid, amt, past_ord, exp_in_days, st, track in active_specs:
        orders_list.append({
            "id": oid,
            "customer_id": cid,
            "product_id": pid,
            "amount": amt,
            "order_date": now - datetime.timedelta(days=past_ord),
            "expected_delivery": now + datetime.timedelta(days=exp_in_days),
            "actual_delivery": None,
            "status": st,
            "tracking_status": track
        })

    # Delivered orders (recent - eligible for return)
    recent_delivered = [
        (1010, 10, 12, 44.99, 7, 3, 3, "Delivered - Left at front door by driver"),
        (1015, 11, 13, 29.99, 8, 4, 4, "Delivered - Signed for by customer"),
        (1022, 13, 14, 24.99, 6, 3, 3, "Delivered - Handed directly to resident"),
        (1025, 14, 15, 39.50, 5, 2, 2, "Delivered - Deposited in secure mail room"),
        (1028, 15, 1, 149.99, 6, 2, 2, "Delivered - Signed for by front desk"),
    ]
    for oid, cid, pid, amt, past_ord, past_exp, past_del, track in recent_delivered:
        orders_list.append({
            "id": oid,
            "customer_id": cid,
            "product_id": pid,
            "amount": amt,
            "order_date": now - datetime.timedelta(days=past_ord),
            "expected_delivery": now - datetime.timedelta(days=past_exp),
            "actual_delivery": now - datetime.timedelta(days=past_del),
            "status": "delivered",
            "tracking_status": track
        })

    # Older Delivered orders
    older_delivered = [
        (1002, 16, 2, 89.50, 25, 20, 20),
        (1003, 17, 3, 49.99, 30, 25, 25),
        (1004, 19, 5, 499.00, 40, 35, 35),
        (1006, 20, 6, 219.00, 22, 18, 18),
        (1007, 1, 7, 119.95, 28, 23, 23),
        (1008, 2, 8, 59.99, 35, 30, 30),
        (1009, 3, 9, 39.99, 50, 45, 45),
        (1011, 4, 10, 129.50, 45, 40, 40),
        (1013, 5, 11, 34.99, 19, 15, 15),
        (1014, 6, 12, 44.99, 21, 16, 16),
        (1016, 7, 14, 24.99, 32, 27, 27),
        (1017, 8, 15, 39.50, 29, 24, 24),
        (1018, 9, 1, 149.99, 60, 55, 55),
        (1019, 10, 2, 89.50, 55, 50, 50),
        (1021, 11, 3, 49.99, 42, 37, 37),
        (1023, 12, 4, 329.00, 38, 33, 33),
        (1024, 13, 5, 499.00, 27, 22, 22),
        (1026, 14, 7, 119.95, 31, 26, 26),
        (1027, 15, 8, 59.99, 24, 19, 19),
        (1029, 16, 10, 129.50, 23, 18, 18),
        (1030, 17, 11, 34.99, 26, 21, 21),
        (1031, 18, 12, 44.99, 28, 23, 23),
        (1032, 19, 13, 29.99, 18, 14, 14),
        (1033, 20, 14, 24.99, 17, 13, 13),
    ]
    for oid, cid, pid, amt, past_ord, past_exp, past_del in older_delivered:
        orders_list.append({
            "id": oid,
            "customer_id": cid,
            "product_id": pid,
            "amount": amt,
            "order_date": now - datetime.timedelta(days=past_ord),
            "expected_delivery": now - datetime.timedelta(days=past_exp),
            "actual_delivery": now - datetime.timedelta(days=past_del),
            "status": "delivered",
            "tracking_status": "Delivered - Package completed successfully"
        })

    for o in orders_list:
        if not db.query(Order).filter(Order.id == o["id"]).first():
            db.add(Order(**o))
    db.commit()

    # 5. Seed Returns (10 returns)
    returns_data = [
        {"id": 1, "order_id": 1002, "reason": "Defective keyboard key switch", "status": "completed", "created_at": now - datetime.timedelta(days=15), "approved_at": now - datetime.timedelta(days=14)},
        {"id": 2, "order_id": 1006, "reason": "Wrong chair color received", "status": "completed", "created_at": now - datetime.timedelta(days=12), "approved_at": now - datetime.timedelta(days=11)},
        {"id": 3, "order_id": 1007, "reason": "Watch screen scratched on arrival", "status": "approved", "created_at": now - datetime.timedelta(days=5), "approved_at": now - datetime.timedelta(days=4)},
        {"id": 4, "order_id": 1008, "reason": "Speaker battery does not charge", "status": "pending", "created_at": now - datetime.timedelta(days=2), "approved_at": None},
        {"id": 5, "order_id": 1011, "reason": "Air purifier filter damaged", "status": "approved", "created_at": now - datetime.timedelta(days=3), "approved_at": now - datetime.timedelta(days=2)},
        {"id": 6, "order_id": 1013, "reason": "Laptop sleeve size too small", "status": "rejected", "created_at": now - datetime.timedelta(days=10), "approved_at": None},
        {"id": 7, "order_id": 1019, "reason": "Item no longer needed", "status": "completed", "created_at": now - datetime.timedelta(days=40), "approved_at": now - datetime.timedelta(days=39)},
        {"id": 8, "order_id": 1024, "reason": "Standing desk motor noise", "status": "pending", "created_at": now - datetime.timedelta(days=1), "approved_at": None},
        {"id": 9, "order_id": 1029, "reason": "Air purifier fan missing screw", "status": "completed", "created_at": now - datetime.timedelta(days=14), "approved_at": now - datetime.timedelta(days=13)},
        {"id": 10, "order_id": 1030, "reason": "Wrong product packaging", "status": "approved", "created_at": now - datetime.timedelta(days=4), "approved_at": now - datetime.timedelta(days=3)},
    ]

    for r in returns_data:
        if not db.query(Return).filter(Return.id == r["id"]).first():
            db.add(Return(**r))
    db.commit()

    # 6. Seed Sample Action Requests & Agent Logs
    if not db.query(ActionRequest).filter(ActionRequest.id == 1).first():
        db.add(ActionRequest(
            id=1,
            action_type="create_return_request",
            payload={"order_id": 1008, "reason": "Speaker battery does not charge", "customer_id": 2},
            status="pending",
            created_at=now - datetime.timedelta(hours=4)
        ))
        db.commit()

    if not db.query(AgentLog).filter(AgentLog.id == 1).first():
        db.add(AgentLog(
            id=1,
            conversation_id="conv-demo-001",
            tool_name="get_delayed_orders",
            input_summary="{}",
            output_summary="Retrieved 6 delayed orders including order 1042",
            status="success",
            timestamp=now - datetime.timedelta(hours=2)
        ))
        db.commit()

    # 7. Seed Customer Issues (8 open issues)
    customer_issues_data = [
        {"id": 1, "customer_id": 1, "order_id": 1042, "issue_type": "delayed", "description": "Package delayed at sorting hub", "status": "open", "created_at": now - datetime.timedelta(days=2)},
        {"id": 2, "customer_id": 2, "order_id": 1001, "issue_type": "delayed", "description": "Carrier vehicle malfunction delay", "status": "open", "created_at": now - datetime.timedelta(days=3)},
        {"id": 3, "customer_id": 5, "order_id": 1005, "issue_type": "delayed", "description": "Weather disruption in transit zone", "status": "open", "created_at": now - datetime.timedelta(days=3)},
        {"id": 4, "customer_id": 8, "order_id": 1012, "issue_type": "delayed", "description": "Address verification exception", "status": "open", "created_at": now - datetime.timedelta(days=1)},
        {"id": 5, "customer_id": 12, "order_id": 1020, "issue_type": "delayed", "description": "Missed hub transfer connection", "status": "open", "created_at": now - datetime.timedelta(days=2)},
        {"id": 6, "customer_id": 18, "order_id": 1035, "issue_type": "delayed", "description": "Logistics depot backlog", "status": "open", "created_at": now - datetime.timedelta(days=4)},
        {"id": 7, "customer_id": 4, "order_id": 1044, "issue_type": "processing", "description": "Warehouse picking in progress", "status": "open", "created_at": now - datetime.timedelta(days=1)},
        {"id": 8, "customer_id": 7, "order_id": 1047, "issue_type": "processing", "description": "Order confirmed awaiting allocation", "status": "open", "created_at": now - datetime.timedelta(days=1)},
    ]
    for issue in customer_issues_data:
        if not db.query(CustomerIssue).filter(CustomerIssue.id == issue["id"]).first():
            db.add(CustomerIssue(**issue))
    db.commit()

    # Sync Postgres sequences if PostgreSQL
    if db.bind and db.bind.dialect.name == "postgresql":
        tables = ["customers", "products", "orders", "inventory", "returns", "action_requests", "agent_logs", "customer_issues"]
        for table in tables:
            try:
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1));"))
            except Exception:
                pass
        db.commit()

    # Sync Postgres sequences if PostgreSQL
    if db.bind and db.bind.dialect.name == "postgresql":
        tables = ["customers", "products", "orders", "inventory", "returns", "action_requests", "agent_logs", "customer_issues"]
        for table in tables:
            try:
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1));"))
            except Exception:
                pass
        db.commit()

    print("Database successfully seeded with 20 customers, 15 products, 15 inventory records, 40 orders, 10 returns, 8 customer issues!")

if __name__ == "__main__":
    db = SessionLocal()
    seed_database(db)
    db.close()
