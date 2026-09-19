import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.models import Customer, Order, Product, Inventory, Return, ActionRequest, AgentLog, CustomerIssue
from app.rag.retriever import policy_rag

def log_agent_tool_call(db: Session, conversation_id: str, tool_name: str, input_data: Any, output_data: Any, status: str = "success"):
    try:
        log_entry = AgentLog(
            conversation_id=conversation_id or "default-session",
            tool_name=tool_name,
            input_summary=str(input_data),
            output_summary=str(output_data)[:1000],  # Truncate if long
            status=status,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"Failed to record agent log: {e}")

# Tool 1: get_order
def get_order_tool(db: Session, order_id: int, conversation_id: str = "default-session") -> Dict[str, Any]:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        res = {"error": f"Order #{order_id} not found."}
        log_agent_tool_call(db, conversation_id, "get_order", {"order_id": order_id}, res, status="error")
        return res

    res = {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "customer_name": order.customer.name if order.customer else "Unknown",
        "product_id": order.product_id,
        "product_name": order.product.name if order.product else "Unknown",
        "amount": order.amount,
        "order_date": order.order_date.isoformat(),
        "expected_delivery": order.expected_delivery.isoformat(),
        "actual_delivery": order.actual_delivery.isoformat() if order.actual_delivery else None,
        "status": order.status,
        "tracking_status": order.tracking_status,
    }
    log_agent_tool_call(db, conversation_id, "get_order", {"order_id": order_id}, res)
    return res

# Tool 2: get_customer
def get_customer_tool(db: Session, customer_id: int, conversation_id: str = "default-session") -> Dict[str, Any]:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        res = {"error": f"Customer #{customer_id} not found."}
        log_agent_tool_call(db, conversation_id, "get_customer", {"customer_id": customer_id}, res, status="error")
        return res

    order_count = db.query(Order).filter(Order.customer_id == customer_id).count()
    
    # Calculate previous returns
    returns_count = db.query(Return).join(Order).filter(Order.customer_id == customer_id).count()
    
    # Delayed/open issue orders
    open_issues = db.query(Order).filter(
        Order.customer_id == customer_id,
        Order.status.in_(["delayed", "processing"])
    ).count()

    res = {
        "customer_id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "order_count": order_count,
        "open_issues": open_issues,
        "previous_return_count": returns_count,
    }
    log_agent_tool_call(db, conversation_id, "get_customer", {"customer_id": customer_id}, res)
    return res

# Tool 3: get_delayed_orders
def get_delayed_orders_tool(db: Session, conversation_id: str = "default-session") -> List[Dict[str, Any]]:
    delayed_orders = db.query(Order).filter(Order.status == "delayed").all()
    now = datetime.datetime.utcnow()

    results = []
    for o in delayed_orders:
        delay_days = (now - o.expected_delivery).days if o.expected_delivery else 0
        results.append({
            "order_id": o.id,
            "customer_id": o.customer_id,
            "customer_name": o.customer.name if o.customer else "Unknown",
            "product_name": o.product.name if o.product else "Unknown",
            "amount": o.amount,
            "expected_delivery": o.expected_delivery.isoformat(),
            "status": o.status,
            "delay_days": max(delay_days, 1),
            "tracking_status": o.tracking_status
        })

    log_agent_tool_call(db, conversation_id, "get_delayed_orders", {}, f"Found {len(results)} delayed orders.")
    return results

# Tool 4: get_low_stock_products
def get_low_stock_products_tool(db: Session, conversation_id: str = "default-session") -> List[Dict[str, Any]]:
    """
    Retrieve products that are low on stock (stock at or below reorder level).
    Use when user asks about: low stock, insufficient inventory, products below reorder level,
    items needing restocking, or inventory shortages.
    """
    items = db.query(Inventory).join(Product).filter(Inventory.stock <= Inventory.reorder_level).all()
    
    results = []
    for inv in items:
        severity = "CRITICAL" if inv.stock == 0 else ("HIGH" if inv.stock <= (inv.reorder_level / 2) else "MEDIUM")
        results.append({
            "product_id": inv.product_id,
            "product_name": inv.product.name,
            "category": inv.product.category,
            "current_stock": inv.stock,
            "reorder_level": inv.reorder_level,
            "severity": severity
        })

    log_agent_tool_call(db, conversation_id, "get_low_stock_products", {}, f"Found {len(results)} low stock products.")
    return results

# Tool 5: get_return_history
def get_return_history_tool(db: Session, order_id: int, conversation_id: str = "default-session") -> List[Dict[str, Any]]:
    returns = db.query(Return).filter(Return.order_id == order_id).all()
    results = []
    for r in returns:
        results.append({
            "return_id": r.id,
            "order_id": r.order_id,
            "reason": r.reason,
            "status": r.status,
            "created_at": r.created_at.isoformat(),
            "approved_at": r.approved_at.isoformat() if r.approved_at else None
        })
    log_agent_tool_call(db, conversation_id, "get_return_history", {"order_id": order_id}, f"Found {len(results)} return records.")
    return results

# Tool 6: check_return_eligibility
def check_return_eligibility_tool(db: Session, order_id: int, reason: str, conversation_id: str = "default-session") -> Dict[str, Any]:
    """
    Evaluate return eligibility for an order based on order status, delivery dates, and return policy.
    An order is eligible ONLY if its status is 'delivered' and delivery was within the return window.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        res = {"is_eligible": False, "reason_summary": f"Order #{order_id} does not exist.", "policy_reference": "N/A"}
        log_agent_tool_call(db, conversation_id, "check_return_eligibility", {"order_id": order_id, "reason": reason}, res)
        return res

    # Retrieve policy chunks from RAG
    policy_chunks = policy_rag.query(f"return policy window damaged item {reason}", top_k=2)
    policy_ref = policy_chunks[0]["content"] if policy_chunks else "Standard 7-day return window policy."

    # Existing active return check
    existing_return = db.query(Return).filter(
        Return.order_id == order_id,
        Return.status.in_(["pending", "approved", "completed"])
    ).first()

    if existing_return:
        res = {
            "order_id": order_id,
            "is_eligible": False,
            "reason_summary": f"Order already has an active or completed return request (#{existing_return.id}, status: {existing_return.status}).",
            "policy_reference": policy_ref,
            "order_status": order.status
        }
        log_agent_tool_call(db, conversation_id, "check_return_eligibility", {"order_id": order_id, "reason": reason}, res)
        return res

    # Consistent Check: Returns require confirmed delivery
    if order.status != "delivered":
        res = {
            "order_id": order_id,
            "is_eligible": False,
            "reason_summary": f"The order has not been marked as delivered (current status: '{order.status}'). The return policy requires confirmed delivery.",
            "policy_reference": policy_ref,
            "order_status": order.status
        }
        log_agent_tool_call(db, conversation_id, "check_return_eligibility", {"order_id": order_id, "reason": reason}, res)
        return res

    # Delivered order date check
    now = datetime.datetime.utcnow()
    delivery_date = order.actual_delivery or order.expected_delivery
    days_since_delivery = (now - delivery_date).days if delivery_date else 0

    is_damaged = "damaged" in reason.lower() or "defective" in reason.lower() or "broken" in reason.lower()
    
    if is_damaged:
        is_eligible = days_since_delivery <= 30  # Damaged item extended grace
        summary = f"Damaged item report within {days_since_delivery} days of delivery (eligible under Damaged Goods Policy)."
    elif days_since_delivery <= 7:
        is_eligible = True
        summary = f"Order delivered {days_since_delivery} days ago (within standard 7-day return window)."
    else:
        is_eligible = False
        summary = f"Order delivered {days_since_delivery} days ago, exceeding standard 7-day return window."

    res = {
        "order_id": order_id,
        "is_eligible": is_eligible,
        "reason_summary": summary,
        "policy_reference": policy_ref,
        "days_since_delivery": days_since_delivery,
        "order_status": order.status
    }
    log_agent_tool_call(db, conversation_id, "check_return_eligibility", {"order_id": order_id, "reason": reason}, res)
    return res

# Tool 7: create_return_request (PROPOSED ACTION ONLY - DOES NOT MUTATE DB DIRECTLY)
def create_return_request_tool(db: Session, order_id: int, reason: str, conversation_id: str = "default-session") -> Dict[str, Any]:
    # Check if order exists
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        res = {"error": f"Order #{order_id} not found."}
        log_agent_tool_call(db, conversation_id, "create_return_request", {"order_id": order_id, "reason": reason}, res, status="error")
        return res

    # Create pending action request record in action_requests table
    action = ActionRequest(
        action_type="create_return_request",
        payload={
            "order_id": order_id,
            "customer_id": order.customer_id,
            "customer_name": order.customer.name if order.customer else "Customer",
            "product_name": order.product.name if order.product else "Product",
            "amount": order.amount,
            "reason": reason
        },
        status="pending",
        created_at=datetime.datetime.utcnow()
    )
    db.add(action)
    db.commit()
    db.refresh(action)

    res = {
        "action_id": action.id,
        "status": "pending_approval",
        "action_type": "create_return_request",
        "message": f"Action proposed: Create return request for Order #{order_id}. Human approval required.",
        "payload": action.payload
    }
    log_agent_tool_call(db, conversation_id, "create_return_request", {"order_id": order_id, "reason": reason}, res, status="pending_approval")
    return res

# Tool 8: draft_customer_message
def draft_customer_message_tool(db: Session, order_id: int, issue_type: str, conversation_id: str = "default-session") -> Dict[str, Any]:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        res = {"error": f"Order #{order_id} not found."}
        log_agent_tool_call(db, conversation_id, "draft_customer_message", {"order_id": order_id, "issue_type": issue_type}, res, status="error")
        return res

    c_name = order.customer.name if order.customer else "Valued Customer"
    p_name = order.product.name if order.product else "your item"

    if issue_type.lower() == "delayed":
        msg = f"Dear {c_name},\n\nWe sincerely apologize for the delay with your order #{order.id} ({p_name}). Our carrier tracking indicates: '{order.tracking_status}'. We are actively monitoring this package to ensure swift delivery. Thank you for your patience.\n\nBest regards,\nUrbanCart Operations Team"
    elif issue_type.lower() in ["damaged", "return_approved"]:
        msg = f"Dear {c_name},\n\nWe have reviewed your request regarding order #{order.id} ({p_name}). A return request has been authorized. You will receive a prepaid shipping label via email shortly.\n\nBest regards,\nUrbanCart Customer Support"
    else:
        msg = f"Dear {c_name},\n\nThank you for contacting UrbanCart regarding order #{order.id} ({p_name}). We have updated your account records and remain at your service for any questions.\n\nBest regards,\nUrbanCart Team"

    res = {
        "order_id": order_id,
        "customer_email": order.customer.email if order.customer else None,
        "issue_type": issue_type,
        "draft_message": msg
    }
    log_agent_tool_call(db, conversation_id, "draft_customer_message", {"order_id": order_id, "issue_type": issue_type}, res)
    return res

# Tool 9: get_operations_summary
def get_operations_summary_tool(db: Session, conversation_id: str = "default-session") -> Dict[str, Any]:
    total_orders = db.query(Order).count()
    delayed_orders = db.query(Order).filter(Order.status == "delayed").count()
    pending_returns = db.query(Return).filter(Return.status == "pending").count()
    low_stock = db.query(Inventory).filter(Inventory.stock <= Inventory.reorder_level).count()
    open_issues = db.query(CustomerIssue).filter(CustomerIssue.status == "open").count()
    if open_issues == 0:
        open_issues = db.query(Order).filter(Order.status.in_(["delayed", "processing"])).count()
    pending_actions_count = db.query(ActionRequest).filter(ActionRequest.status == "pending").count()

    alerts = []
    if delayed_orders > 0:
        alerts.append({"type": "warning", "title": "Delayed Shipments Alert", "message": f"{delayed_orders} orders are currently experiencing carrier delays."})
    if low_stock > 0:
        alerts.append({"type": "critical", "title": "Low Inventory Alert", "message": f"{low_stock} products are below critical reorder thresholds."})
    if pending_actions_count > 0:
        alerts.append({"type": "info", "title": "Action Approvals Pending", "message": f"{pending_actions_count} proposed operational actions await human sign-off."})

    res = {
        "total_orders": total_orders,
        "delayed_orders": delayed_orders,
        "pending_returns": pending_returns,
        "low_stock_products": low_stock,
        "open_customer_issues": open_issues,
        "pending_actions_count": pending_actions_count,
        "recent_alerts": alerts
    }
    log_agent_tool_call(db, conversation_id, "get_operations_summary", {}, res)
    return res
