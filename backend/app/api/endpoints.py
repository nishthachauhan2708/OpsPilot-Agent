import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Customer, Order, Product, Inventory, Return, ActionRequest, AgentLog
from app.schemas.domain import (
    CustomerRead,
    OrderRead,
    InventoryRead,
    ReturnRead,
    ReturnEligibilityCheck,
    ReturnEligibilityResponse,
    ActionRequestRead,
    AgentLogRead,
    AnalyticsSummary,
    AgentChatRequest,
    AgentChatResponse
)
from app.tools.ops_tools import (
    get_order_tool,
    get_customer_tool,
    get_delayed_orders_tool,
    get_low_stock_products_tool,
    get_return_history_tool,
    check_return_eligibility_tool,
    get_operations_summary_tool
)
from app.agents.ops_agent import ops_agent_engine
from app.api.import_router import import_router

router = APIRouter()
router.include_router(import_router)

@router.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend operational status."""
    return {"status": "ok", "service": "OpsPilot Operations Engine", "timestamp": datetime.datetime.utcnow().isoformat()}

@router.get("/analytics/summary", response_model=AnalyticsSummary, tags=["Analytics"])
def get_analytics_summary(db: Session = Depends(get_db)):
    """Retrieve operational dashboard overview metrics."""
    res = get_operations_summary_tool(db)
    return AnalyticsSummary(
        total_orders=res["total_orders"],
        delayed_orders=res["delayed_orders"],
        pending_returns=res["pending_returns"],
        low_stock_products=res["low_stock_products"],
        open_customer_issues=res["open_customer_issues"],
        recent_alerts=res["recent_alerts"]
    )

@router.get("/orders", response_model=List[OrderRead], tags=["Orders"])
def get_all_orders(db: Session = Depends(get_db)):
    """Retrieve all orders in the system."""
    orders = db.query(Order).order_by(Order.order_date.desc()).all()
    results = []
    for o in orders:
        results.append(OrderRead(
            id=o.id,
            customer_id=o.customer_id,
            product_id=o.product_id,
            amount=o.amount,
            order_date=o.order_date,
            expected_delivery=o.expected_delivery,
            actual_delivery=o.actual_delivery,
            status=o.status,
            tracking_status=o.tracking_status,
            customer_name=o.customer.name if o.customer else "Unknown",
            product_name=o.product.name if o.product else "Unknown"
        ))
    return results

@router.get("/orders/delayed", response_model=List[OrderRead], tags=["Orders"])
def get_delayed_orders(db: Session = Depends(get_db)):
    """Retrieve all delayed orders in the system."""
    delayed = db.query(Order).filter(Order.status == "delayed").all()
    results = []
    for o in delayed:
        results.append(OrderRead(
            id=o.id,
            customer_id=o.customer_id,
            product_id=o.product_id,
            amount=o.amount,
            order_date=o.order_date,
            expected_delivery=o.expected_delivery,
            actual_delivery=o.actual_delivery,
            status=o.status,
            tracking_status=o.tracking_status,
            customer_name=o.customer.name if o.customer else "Unknown",
            product_name=o.product.name if o.product else "Unknown"
        ))
    return results

@router.get("/orders/{order_id}", response_model=OrderRead, tags=["Orders"])
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed order record by order ID."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found.")
    return OrderRead(
        id=order.id,
        customer_id=order.customer_id,
        product_id=order.product_id,
        amount=order.amount,
        order_date=order.order_date,
        expected_delivery=order.expected_delivery,
        actual_delivery=order.actual_delivery,
        status=order.status,
        tracking_status=order.tracking_status,
        customer_name=order.customer.name if order.customer else "Unknown",
        product_name=order.product.name if order.product else "Unknown"
    )

@router.get("/customers/{customer_id}", response_model=CustomerRead, tags=["Customers"])
def get_customer_by_id(customer_id: int, db: Session = Depends(get_db)):
    """Retrieve customer details by ID."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer #{customer_id} not found.")
    return customer

@router.get("/inventory/low-stock", response_model=List[InventoryRead], tags=["Inventory"])
def get_low_stock_inventory(db: Session = Depends(get_db)):
    """Retrieve inventory items at or below reorder thresholds."""
    items = db.query(Inventory).join(Product).filter(Inventory.stock <= Inventory.reorder_level).all()
    results = []
    for inv in items:
        results.append(InventoryRead(
            id=inv.id,
            product_id=inv.product_id,
            product_name=inv.product.name,
            stock=inv.stock,
            reorder_level=inv.reorder_level,
            is_low_stock=inv.stock <= inv.reorder_level
        ))
    return results

@router.get("/returns/{order_id}", response_model=List[ReturnRead], tags=["Returns"])
def get_returns_by_order(order_id: int, db: Session = Depends(get_db)):
    """Retrieve return request records for a specific order."""
    returns = db.query(Return).filter(Return.order_id == order_id).all()
    results = []
    for r in returns:
        order = db.query(Order).filter(Order.id == r.order_id).first()
        results.append(ReturnRead(
            id=r.id,
            order_id=r.order_id,
            reason=r.reason,
            status=r.status,
            created_at=r.created_at,
            approved_at=r.approved_at,
            customer_name=order.customer.name if order and order.customer else None,
            product_name=order.product.name if order and order.product else None
        ))
    return results

@router.get("/returns", response_model=List[ReturnRead], tags=["Returns"])
def get_all_returns(db: Session = Depends(get_db)):
    """Retrieve all return requests in system."""
    returns = db.query(Return).order_by(Return.created_at.desc()).all()
    results = []
    for r in returns:
        order = db.query(Order).filter(Order.id == r.order_id).first()
        results.append(ReturnRead(
            id=r.id,
            order_id=r.order_id,
            reason=r.reason,
            status=r.status,
            created_at=r.created_at,
            approved_at=r.approved_at,
            customer_name=order.customer.name if order and order.customer else None,
            product_name=order.product.name if order and order.product else None
        ))
    return results

@router.post("/returns/check-eligibility", response_model=ReturnEligibilityResponse, tags=["Returns"])
def check_eligibility(req: ReturnEligibilityCheck, db: Session = Depends(get_db)):
    """Evaluate return eligibility for an order based on delivery dates and company policy."""
    res = check_return_eligibility_tool(db, req.order_id, req.reason)
    return ReturnEligibilityResponse(
        order_id=req.order_id,
        is_eligible=res.get("is_eligible", False),
        reason_summary=res.get("reason_summary", ""),
        policy_reference=res.get("policy_reference", ""),
        days_since_delivery=res.get("days_since_delivery"),
        order_status=res.get("order_status", "unknown")
    )

@router.get("/actions/pending", response_model=List[ActionRequestRead], tags=["Human Approval"])
def get_pending_actions(db: Session = Depends(get_db)):
    """Get all proposed write actions awaiting human review."""
    actions = db.query(ActionRequest).filter(ActionRequest.status == "pending").all()
    return actions

@router.post("/actions/{action_id}/approve", response_model=ActionRequestRead, tags=["Human Approval"])
def approve_action(action_id: int, db: Session = Depends(get_db)):
    """
    HUMAN-IN-THE-LOOP APPROVAL ENDPOINT.
    Executes database mutation for the pending write action.
    """
    action = db.query(ActionRequest).filter(ActionRequest.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail=f"Action Request #{action_id} not found.")

    if action.status != "pending":
        raise HTTPException(status_code=400, detail=f"Action #{action_id} is already in '{action.status}' state.")

    # Sync postgres sequence if running on PostgreSQL to prevent primary key collision
    if db.bind and db.bind.dialect.name == "postgresql":
        from sqlalchemy import text
        for tbl in ["returns", "agent_logs", "action_requests"]:
            try:
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE((SELECT MAX(id) FROM {tbl}), 1));"))
            except Exception:
                pass
        db.commit()

    # Execute action based on action_type
    if action.action_type == "create_return_request":
        payload = action.payload or {}
        order_id = payload.get("order_id")
        reason = payload.get("reason", "Approved return request")

        # Mutate Database: create return record
        new_return = Return(
            order_id=order_id,
            reason=reason,
            status="approved",
            created_at=datetime.datetime.utcnow(),
            approved_at=datetime.datetime.utcnow()
        )
        db.add(new_return)
        
        # Update action status
        action.status = "approved"
        action.reviewed_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(action)

        # Record Agent Log
        try:
            log_entry = AgentLog(
                conversation_id="human-approval-system",
                tool_name="approve_action_executed",
                input_summary=f"Action ID: {action_id}",
                output_summary=f"Mutated DB: Created Return #{new_return.id} for Order #{order_id}",
                status="success",
                timestamp=datetime.datetime.utcnow()
            )
            db.add(log_entry)
            db.commit()
        except Exception:
            pass

        return action
    else:
        action.status = "approved"
        action.reviewed_at = datetime.datetime.utcnow()
        db.commit()
        return action

@router.post("/actions/{action_id}/reject", response_model=ActionRequestRead, tags=["Human Approval"])
def reject_action(action_id: int, db: Session = Depends(get_db)):
    """Reject a proposed write action (prevents database mutation)."""
    action = db.query(ActionRequest).filter(ActionRequest.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail=f"Action Request #{action_id} not found.")

    action.status = "rejected"
    action.reviewed_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(action)

    log_entry = AgentLog(
        conversation_id="human-approval-system",
        tool_name="reject_action_executed",
        input_summary=f"Action ID: {action_id}",
        output_summary=f"Action #{action_id} rejected by human operator. No database mutation.",
        status="rejected",
        timestamp=datetime.datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()

    return action

@router.post("/agent/chat", response_model=AgentChatResponse, tags=["Agent Workspace"])
def agent_chat(req: AgentChatRequest, db: Session = Depends(get_db)):
    """Main Agent Conversation endpoint."""
    res = ops_agent_engine.run(db, req.message, req.conversation_id)
    return AgentChatResponse(
        conversation_id=res["conversation_id"],
        message=res["message"],
        tool_events=res.get("tool_events", []),
        pending_action=res.get("pending_action")
    )

@router.get("/agent/logs", response_model=List[AgentLogRead], tags=["Observability"])
def get_agent_logs(db: Session = Depends(get_db)):
    """Retrieve audit log of agent tool calls and executions."""
    logs = db.query(AgentLog).order_by(AgentLog.timestamp.desc()).limit(100).all()
    return logs
