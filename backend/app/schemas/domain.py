from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
import datetime

class CustomerRead(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class ProductRead(BaseModel):
    id: int
    name: str
    category: str
    price: float

    model_config = ConfigDict(from_attributes=True)

class OrderRead(BaseModel):
    id: int
    customer_id: int
    product_id: int
    amount: float
    order_date: datetime.datetime
    expected_delivery: datetime.datetime
    actual_delivery: Optional[datetime.datetime] = None
    status: str
    tracking_status: str
    customer_name: Optional[str] = None
    product_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class InventoryRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    stock: int
    reorder_level: int
    is_low_stock: bool

    model_config = ConfigDict(from_attributes=True)

class ReturnRead(BaseModel):
    id: int
    order_id: int
    reason: str
    status: str
    created_at: datetime.datetime
    approved_at: Optional[datetime.datetime] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReturnEligibilityCheck(BaseModel):
    order_id: int
    reason: str

class ReturnEligibilityResponse(BaseModel):
    order_id: int
    is_eligible: bool
    reason_summary: str
    policy_reference: str
    days_since_delivery: Optional[int] = None
    order_status: str

class ActionRequestRead(BaseModel):
    id: int
    action_type: str
    payload: Dict[str, Any]
    status: str
    created_at: datetime.datetime
    reviewed_at: Optional[datetime.datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AgentLogRead(BaseModel):
    id: int
    conversation_id: str
    tool_name: str
    input_summary: str
    output_summary: str
    status: str
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class AnalyticsSummary(BaseModel):
    total_orders: int
    delayed_orders: int
    pending_returns: int
    low_stock_products: int
    open_customer_issues: int
    recent_alerts: List[Dict[str, Any]]

class ToolEvent(BaseModel):
    tool_name: str
    status: str  # 'started', 'completed', 'failed', 'pending_approval'
    input: Dict[str, Any]
    output: Any
    description: str

class AgentChatRequest(BaseModel):
    message: str
    conversation_id: str = "default-session"

class AgentChatResponse(BaseModel):
    conversation_id: str
    message: str
    tool_events: List[ToolEvent] = []
    pending_action: Optional[ActionRequestRead] = None
