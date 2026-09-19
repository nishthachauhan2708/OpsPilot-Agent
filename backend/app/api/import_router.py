import csv
import io
import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.database.models import Customer, Product, Order, Inventory, Return, CustomerIssue, ActionRequest, AgentLog

import_router = APIRouter(prefix="/import", tags=["Company Data Import"])

def parse_date(date_str: Optional[str]) -> Optional[datetime.datetime]:
    if not date_str or not date_str.strip():
        return None
    val = date_str.strip()
    # Try ISO format
    try:
        return datetime.datetime.fromisoformat(val.replace("Z", "+00:00"))
    except Exception:
        pass
    # Try YYYY-MM-DD
    try:
        return datetime.datetime.strptime(val, "%Y-%m-%d")
    except Exception:
        pass
    # Try YYYY-MM-DD HH:MM:SS
    try:
        return datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def sync_postgres_sequence(db: Session, table_name: str):
    if db.bind and db.bind.dialect.name == "postgresql":
        try:
            db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE((SELECT MAX(id) FROM {table_name}), 1));"))
            db.commit()
        except Exception:
            pass

@import_router.get("/template/{data_type}")
def get_import_template(data_type: str):
    dt = data_type.lower().replace("_", "-")
    templates = {
        "orders": "id,customer_id,product_id,amount,order_date,expected_delivery,actual_delivery,status,tracking_status\n2001,1,1,149.99,2026-09-10T10:00:00,2026-09-15T10:00:00,,delayed,In Transit - Delayed at sorting hub\n",
        "inventory": "product_id,product_name,category,price,stock,reorder_level\n1,AuraSound Wireless Noise-Canceling Headphones,Electronics,149.99,45,15\n",
        "returns": "id,order_id,reason,status,created_at,approved_at\n101,1002,Defective keyboard key switch,completed,2026-09-01T12:00:00,2026-09-02T12:00:00\n",
        "customers": "id,name,email,created_at\n101,Aarav Sharma,aarav.sharma@example.com,2026-08-20T10:00:00\n",
        "customer-issues": "id,customer_id,order_id,issue_type,description,status,created_at\n101,1,1042,delayed,Package delayed in transit for over 4 days,open\n"
    }
    if dt not in templates:
        raise HTTPException(status_code=404, detail=f"Template for '{data_type}' not found.")
    
    return Response(
        content=templates[dt],
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={dt}_template.csv"}
    )

@import_router.post("/orders")
async def import_orders(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.csv', '.txt', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8-sig")
    except Exception:
        decoded = contents.decode("latin-1")
    
    reader = csv.DictReader(io.StringIO(decoded))
    imported, updated, skipped = 0, 0, 0
    errors = []

    for row_idx, row in enumerate(reader, start=2):
        cleaned = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
        try:
            order_id = int(cleaned["id"]) if cleaned.get("id") else None
            customer_id = int(cleaned.get("customer_id", 0))
            product_id = int(cleaned.get("product_id", 0))
            amount = float(cleaned.get("amount", 0.0))
            status_str = cleaned.get("status", "processing").lower()
            tracking = cleaned.get("tracking_status", "Order Processing")
            
            if not customer_id or not product_id:
                errors.append(f"Row {row_idx}: Missing customer_id or product_id.")
                skipped += 1
                continue
            
            # Verify customer & product exist
            cust = db.query(Customer).filter(Customer.id == customer_id).first()
            prod = db.query(Product).filter(Product.id == product_id).first()
            if not cust or not prod:
                errors.append(f"Row {row_idx}: Customer #{customer_id} or Product #{product_id} not found in database.")
                skipped += 1
                continue

            order_date = parse_date(cleaned.get("order_date")) or datetime.datetime.utcnow()
            expected = parse_date(cleaned.get("expected_delivery")) or (order_date + datetime.timedelta(days=5))
            actual = parse_date(cleaned.get("actual_delivery"))

            existing = None
            if order_id:
                existing = db.query(Order).filter(Order.id == order_id).first()

            if existing:
                existing.customer_id = customer_id
                existing.product_id = product_id
                existing.amount = amount
                existing.order_date = order_date
                existing.expected_delivery = expected
                existing.actual_delivery = actual
                existing.status = status_str
                existing.tracking_status = tracking
                updated += 1
            else:
                new_ord = Order(
                    id=order_id,
                    customer_id=customer_id,
                    product_id=product_id,
                    amount=amount,
                    order_date=order_date,
                    expected_delivery=expected,
                    actual_delivery=actual,
                    status=status_str,
                    tracking_status=tracking
                ) if order_id else Order(
                    customer_id=customer_id,
                    product_id=product_id,
                    amount=amount,
                    order_date=order_date,
                    expected_delivery=expected,
                    actual_delivery=actual,
                    status=status_str,
                    tracking_status=tracking
                )
                db.add(new_ord)
                imported += 1

        except Exception as e:
            errors.append(f"Row {row_idx}: Invalid data format ({str(e)})")
            skipped += 1

    db.commit()
    sync_postgres_sequence(db, "orders")

    return {
        "success": True,
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors
    }

@import_router.post("/inventory")
async def import_inventory(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.csv', '.txt', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8-sig")
    except Exception:
        decoded = contents.decode("latin-1")
    
    reader = csv.DictReader(io.StringIO(decoded))
    imported, updated, skipped = 0, 0, 0
    errors = []

    for row_idx, row in enumerate(reader, start=2):
        cleaned = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
        try:
            prod_id = int(cleaned["product_id"]) if cleaned.get("product_id") else (int(cleaned["id"]) if cleaned.get("id") else None)
            prod_name = cleaned.get("product_name") or cleaned.get("name") or "Standard Item"
            category = cleaned.get("category", "General")
            price = float(cleaned.get("price", 19.99))
            stock = int(cleaned.get("stock", 0))
            reorder_level = int(cleaned.get("reorder_level", 10))

            if not prod_id:
                errors.append(f"Row {row_idx}: Missing product_id.")
                skipped += 1
                continue

            prod = db.query(Product).filter(Product.id == prod_id).first()
            if not prod:
                prod = Product(id=prod_id, name=prod_name, category=category, price=price)
                db.add(prod)
                db.commit()
            else:
                if cleaned.get("product_name"):
                    prod.name = prod_name
                if cleaned.get("category"):
                    prod.category = category
                if cleaned.get("price"):
                    prod.price = price

            inv = db.query(Inventory).filter(Inventory.product_id == prod_id).first()
            if inv:
                inv.stock = stock
                inv.reorder_level = reorder_level
                updated += 1
            else:
                new_inv = Inventory(product_id=prod_id, stock=stock, reorder_level=reorder_level)
                db.add(new_inv)
                imported += 1

        except Exception as e:
            errors.append(f"Row {row_idx}: Invalid data ({str(e)})")
            skipped += 1

    db.commit()
    sync_postgres_sequence(db, "inventory")
    sync_postgres_sequence(db, "products")

    return {
        "success": True,
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors
    }

@import_router.post("/returns")
async def import_returns(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.csv', '.txt', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8-sig")
    except Exception:
        decoded = contents.decode("latin-1")
    
    reader = csv.DictReader(io.StringIO(decoded))
    imported, updated, skipped = 0, 0, 0
    errors = []

    for row_idx, row in enumerate(reader, start=2):
        cleaned = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
        try:
            return_id = int(cleaned["id"]) if cleaned.get("id") else None
            order_id = int(cleaned.get("order_id", 0))
            reason = cleaned.get("reason", "Customer return")
            status_str = cleaned.get("status", "pending").lower()
            created_at = parse_date(cleaned.get("created_at")) or datetime.datetime.utcnow()
            approved_at = parse_date(cleaned.get("approved_at"))

            if not order_id:
                errors.append(f"Row {row_idx}: Missing order_id.")
                skipped += 1
                continue

            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                errors.append(f"Row {row_idx}: Order #{order_id} not found in database.")
                skipped += 1
                continue

            existing = None
            if return_id:
                existing = db.query(Return).filter(Return.id == return_id).first()
            else:
                existing = db.query(Return).filter(Return.order_id == order_id, Return.reason == reason).first()

            if existing:
                existing.reason = reason
                existing.status = status_str
                existing.approved_at = approved_at
                updated += 1
            else:
                new_ret = Return(
                    id=return_id,
                    order_id=order_id,
                    reason=reason,
                    status=status_str,
                    created_at=created_at,
                    approved_at=approved_at
                ) if return_id else Return(
                    order_id=order_id,
                    reason=reason,
                    status=status_str,
                    created_at=created_at,
                    approved_at=approved_at
                )
                db.add(new_ret)
                imported += 1

        except Exception as e:
            errors.append(f"Row {row_idx}: Invalid data ({str(e)})")
            skipped += 1

    db.commit()
    sync_postgres_sequence(db, "returns")

    return {
        "success": True,
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors
    }

@import_router.post("/customers")
async def import_customers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.csv', '.txt', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8-sig")
    except Exception:
        decoded = contents.decode("latin-1")
    
    reader = csv.DictReader(io.StringIO(decoded))
    imported, updated, skipped = 0, 0, 0
    errors = []

    for row_idx, row in enumerate(reader, start=2):
        cleaned = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
        try:
            cust_id = int(cleaned["id"]) if cleaned.get("id") else None
            name = cleaned.get("name", "Unknown Customer")
            email = cleaned.get("email", "").lower()
            created_at = parse_date(cleaned.get("created_at")) or datetime.datetime.utcnow()

            if not email:
                errors.append(f"Row {row_idx}: Missing email address.")
                skipped += 1
                continue

            existing = None
            if cust_id:
                existing = db.query(Customer).filter(Customer.id == cust_id).first()
            if not existing:
                existing = db.query(Customer).filter(Customer.email == email).first()

            if existing:
                existing.name = name
                existing.email = email
                updated += 1
            else:
                new_cust = Customer(id=cust_id, name=name, email=email, created_at=created_at) if cust_id else Customer(name=name, email=email, created_at=created_at)
                db.add(new_cust)
                imported += 1

        except Exception as e:
            errors.append(f"Row {row_idx}: Invalid data ({str(e)})")
            skipped += 1

    db.commit()
    sync_postgres_sequence(db, "customers")

    return {
        "success": True,
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors
    }

@import_router.post("/customer-issues")
async def import_customer_issues(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.csv', '.txt', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8-sig")
    except Exception:
        decoded = contents.decode("latin-1")
    
    reader = csv.DictReader(io.StringIO(decoded))
    imported, updated, skipped = 0, 0, 0
    errors = []

    for row_idx, row in enumerate(reader, start=2):
        cleaned = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
        try:
            issue_id = int(cleaned["id"]) if cleaned.get("id") else None
            cust_id = int(cleaned["customer_id"]) if cleaned.get("customer_id") else None
            ord_id = int(cleaned["order_id"]) if cleaned.get("order_id") else None
            issue_type = cleaned.get("issue_type", "general")
            description = cleaned.get("description", "Customer support issue")
            status_str = cleaned.get("status", "open").lower()
            created_at = parse_date(cleaned.get("created_at")) or datetime.datetime.utcnow()

            existing = None
            if issue_id:
                existing = db.query(CustomerIssue).filter(CustomerIssue.id == issue_id).first()

            if existing:
                existing.issue_type = issue_type
                existing.description = description
                existing.status = status_str
                if cust_id:
                    existing.customer_id = cust_id
                if ord_id:
                    existing.order_id = ord_id
                updated += 1
            else:
                new_issue = CustomerIssue(
                    id=issue_id,
                    customer_id=cust_id,
                    order_id=ord_id,
                    issue_type=issue_type,
                    description=description,
                    status=status_str,
                    created_at=created_at
                ) if issue_id else CustomerIssue(
                    customer_id=cust_id,
                    order_id=ord_id,
                    issue_type=issue_type,
                    description=description,
                    status=status_str,
                    created_at=created_at
                )
                db.add(new_issue)
                imported += 1

        except Exception as e:
            errors.append(f"Row {row_idx}: Invalid data ({str(e)})")
            skipped += 1

    db.commit()
    sync_postgres_sequence(db, "customer_issues")

    return {
        "success": True,
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors
    }
