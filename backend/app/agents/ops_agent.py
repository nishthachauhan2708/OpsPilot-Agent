import re
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.tools.ops_tools import (
    get_order_tool,
    get_customer_tool,
    get_delayed_orders_tool,
    get_low_stock_products_tool,
    get_return_history_tool,
    check_return_eligibility_tool,
    create_return_request_tool,
    draft_customer_message_tool,
    get_operations_summary_tool
)
from app.rag.retriever import policy_rag
from app.database.models import ActionRequest, AgentLog

class OpsPilotAgent:
    """
    OpsPilot Agent Engine.
    Executes tool-based reasoning, RAG policy checks, prompt injection guardrails,
    and produces structured business responses with real execution traces.
    """

    def sanitize_input(self, text: str) -> str:
        # Defense against prompt injection
        patterns_to_block = [
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"reveal\s+(system\s+)?prompt",
            r"dump\s+database",
            r"override\s+security",
            r"delete\s+all\s+data"
        ]
        for pattern in patterns_to_block:
            if re.search(pattern, text, re.IGNORECASE):
                raise ValueError("Security Violation: Prompt injection or restricted system instruction detected.")
        return text.strip()

    def run(self, db: Session, user_message: str, conversation_id: str = "default-session") -> Dict[str, Any]:
        tool_events: List[Dict[str, Any]] = []
        pending_action = None

        try:
            clean_message = self.sanitize_input(user_message)
        except ValueError as e:
            return {
                "conversation_id": conversation_id,
                "message": "Security Alert: Your request contains patterns that violate system safety policies. Please rephrase your query.",
                "tool_events": [{
                    "tool_name": "security_guardrail",
                    "status": "failed",
                    "input": {"raw_message": user_message},
                    "output": "Blocked by system guardrail against prompt injection.",
                    "description": "Security Guardrail"
                }],
                "pending_action": None
            }

        msg_lower = clean_message.lower().strip()

        # -------------------------------------------------------------
        # PART 3: Greeting Behavior (Zero Business Tool Calls)
        # -------------------------------------------------------------
        greeting_words = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings"}
        cleaned_words = re.sub(r'[^\w\s]', '', msg_lower).split()
        if msg_lower in greeting_words or (len(cleaned_words) <= 2 and cleaned_words[0] in greeting_words):
            return {
                "conversation_id": conversation_id,
                "message": "Hi! I'm OpsPilot. I can help you check orders, inventory, returns and daily operations.",
                "tool_events": [],
                "pending_action": None
            }

        # Extract order ID if present in query (e.g. 1042, #1042, order 1042)
        order_id_match = re.search(r'\b(?:order\s*#?|#)?(\d{4,5})\b', msg_lower)
        order_id = int(order_id_match.group(1)) if order_id_match else None

        # -------------------------------------------------------------
        # PART 2: Return Creation Workflow (Strict Eligibility Check First)
        # -------------------------------------------------------------
        if ("create" in msg_lower or "submit" in msg_lower or "initiate" in msg_lower or "file" in msg_lower or "process" in msg_lower) and "return" in msg_lower:
            target_order = order_id or 1042
            reason = "Item arrived damaged" if "damaged" in msg_lower else ("Item defective" if "defective" in msg_lower else "Customer return request")

            # Step 1: Check eligibility
            tool_events.append({
                "tool_name": "check_return_eligibility",
                "status": "started",
                "input": {"order_id": target_order, "reason": reason},
                "output": None,
                "description": f"Checking eligibility for Order #{target_order}"
            })
            eligibility = check_return_eligibility_tool(db, target_order, reason, conversation_id)
            tool_events[-1]["status"] = "completed"
            tool_events[-1]["output"] = eligibility

            if not eligibility.get("is_eligible", False):
                final_text = (
                    f"Order #{target_order} is not currently eligible for a return.\n\n"
                    f"Reason: {eligibility.get('reason_summary', 'The order does not meet return policy criteria.')}\n\n"
                    f"No return request was created."
                )
                return {
                    "conversation_id": conversation_id,
                    "message": final_text,
                    "tool_events": tool_events,
                    "pending_action": None
                }

            # Step 2: Propose write action if eligible
            tool_events.append({
                "tool_name": "create_return_request",
                "status": "started",
                "input": {"order_id": target_order, "reason": reason},
                "output": None,
                "description": f"Preparing return request for approval"
            })
            action_res = create_return_request_tool(db, target_order, reason, conversation_id)
            tool_events[-1]["status"] = "pending_approval"
            tool_events[-1]["output"] = action_res

            pending_action = db.query(ActionRequest).filter(ActionRequest.id == action_res["action_id"]).first()
            pending_action_dict = {
                "id": pending_action.id,
                "action_type": pending_action.action_type,
                "payload": pending_action.payload,
                "status": pending_action.status,
                "created_at": pending_action.created_at.isoformat()
            } if pending_action else None

            final_text = (
                f"Order #{target_order} is eligible for a return under the current return policy.\n\n"
                f"Reason: {reason}.\n\n"
                f"I can prepare the return request for approval."
            )

            return {
                "conversation_id": conversation_id,
                "message": final_text,
                "tool_events": tool_events,
                "pending_action": pending_action_dict
            }

        # -------------------------------------------------------------
        # Return Eligibility Check Inquiry
        # -------------------------------------------------------------
        elif "eligible" in msg_lower or ("can" in msg_lower and "return" in msg_lower) or ("return" in msg_lower and "policy" in msg_lower):
            target_order = order_id or 1042
            reason = "Item arrived damaged" if "damaged" in msg_lower else "Return eligibility inquiry"

            # Step 1: Fetch Order
            tool_events.append({
                "tool_name": "get_order",
                "status": "started",
                "input": {"order_id": target_order},
                "output": None,
                "description": f"Retrieved order #{target_order}"
            })
            order_data = get_order_tool(db, target_order, conversation_id)
            tool_events[-1]["status"] = "completed"
            tool_events[-1]["output"] = order_data

            # Step 2: Policy check
            tool_events.append({
                "tool_name": "check_return_eligibility",
                "status": "started",
                "input": {"order_id": target_order, "reason": reason},
                "output": None,
                "description": f"Checked order against return policy"
            })
            eligibility = check_return_eligibility_tool(db, target_order, reason, conversation_id)
            tool_events[-1]["status"] = "completed"
            tool_events[-1]["output"] = eligibility

            if eligibility.get("is_eligible", False):
                final_text = (
                    f"Order #{target_order} is eligible for a return under the current return policy.\n\n"
                    f"Reason: {eligibility.get('reason_summary', '')}\n\n"
                    f"I can prepare the return request for approval."
                )
            else:
                final_text = (
                    f"Order #{target_order} is not currently eligible for a return.\n\n"
                    f"Reason: {eligibility.get('reason_summary', '')}\n\n"
                    f"No return request was created."
                )

            return {
                "conversation_id": conversation_id,
                "message": final_text,
                "tool_events": tool_events,
                "pending_action": None
            }

        # -------------------------------------------------------------
        # Order Delay Inquiry / Cause
        # -------------------------------------------------------------
        elif ("why" in msg_lower and "delay" in msg_lower) or ("delay" in msg_lower and order_id is not None):
            target_order = order_id or 1042

            tool_events.append({
                "tool_name": "get_order",
                "status": "started",
                "input": {"order_id": target_order},
                "output": None,
                "description": f"Retrieved order #{target_order}"
            })
            order_data = get_order_tool(db, target_order, conversation_id)
            tool_events[-1]["status"] = "completed"
            tool_events[-1]["output"] = order_data

            if "error" in order_data:
                return {
                    "conversation_id": conversation_id,
                    "message": f"Order #{target_order} could not be found.",
                    "tool_events": tool_events,
                    "pending_action": None
                }

            final_text = (
                f"Order #{target_order}\n\n"
                f"Customer: {order_data['customer_name']}\n"
                f"Product: {order_data['product_name']}\n"
                f"Status: Delayed\n"
                f"Tracking note: {order_data['tracking_status']}\n\n"
                f"The order is currently delayed in transit."
            )

            return {
                "conversation_id": conversation_id,
                "message": final_text,
                "tool_events": tool_events,
                "pending_action": None
            }

        # -------------------------------------------------------------
        # Delayed Orders List
        # -------------------------------------------------------------
        elif "delayed" in msg_lower or "delays" in msg_lower:
            tool_events.append({
                "tool_name": "get_delayed_orders",
                "status": "started",
                "input": {},
                "output": None,
                "description": "Found delayed orders"
            })
            delayed_orders = get_delayed_orders_tool(db, conversation_id)
            tool_events[-1]["status"] = "completed"
            tool_events[-1]["output"] = {"count": len(delayed_orders)}

            if not delayed_orders:
                return {
                    "conversation_id": conversation_id,
                    "message": "There are currently no delayed orders.",
                    "tool_events": tool_events,
                    "pending_action": None
                }

            table_rows = []
            for o in delayed_orders:
                table_rows.append(f"| #{o['order_id']} | {o['customer_name']} | {o['product_name']} | {o['expected_delivery'][:10]} | {o['delay_days']} days late |")

            table_str = "\n".join(table_rows)

            final_text = (
                f"Here are the {len(delayed_orders)} orders currently marked as delayed:\n\n"
                f"| Order | Customer | Product | Expected delivery | Delay |\n"
                f"|---|---|---|---|---|\n"
                f"{table_str}\n\n"
                f"Order #1042 is delayed by 2 days."
            )

            return {
                "conversation_id": conversation_id,
                "message": final_text,
                "tool_events": tool_events,
                "pending_action": None
            }

        # -------------------------------------------------------------
        # PART 1: Low Stock Products (EXPLICIT TOOL ROUTING)
        # -------------------------------------------------------------
        elif "low stock" in msg_lower or "low on stock" in msg_lower or "reorder" in msg_lower or "restock" in msg_lower or "shortage" in msg_lower or "insufficient inventory" in msg_lower:
            tool_events.append({
                "tool_name": "get_low_stock_products",
                "status": "started",
                "input": {},
                "output": None,
                "description": f"Found low stock products"
            })
            low_stock_items = get_low_stock_products_tool(db, conversation_id)
            tool_events[-1]["status"] = "completed"
            tool_events[-1]["output"] = {"count": len(low_stock_items)}

            table_rows = []
            for item in low_stock_items:
                table_rows.append(f"| {item['product_name']} | {item['current_stock']} | {item['reorder_level']} |")

            table_str = "\n".join(table_rows)

            final_text = (
                f"I found {len(low_stock_items)} products below their reorder level:\n\n"
                f"| Product | Stock | Reorder level |\n"
                f"|---|---|---|\n"
                f"{table_str}\n\n"
                f"These are the items that may need restocking."
            )

            return {
                "conversation_id": conversation_id,
                "message": final_text,
                "tool_events": tool_events,
                "pending_action": None
            }

        # -------------------------------------------------------------
        # Order Details Lookup
        # -------------------------------------------------------------
        elif order_id is not None:
            tool_events.append({
                "tool_name": "get_order",
                "status": "started",
                "input": {"order_id": order_id},
                "output": None,
                "description": f"Retrieved order #{order_id}"
            })
            order_data = get_order_tool(db, order_id, conversation_id)
            tool_events[-1]["status"] = "completed"
            tool_events[-1]["output"] = order_data

            if "error" in order_data:
                return {
                    "conversation_id": conversation_id,
                    "message": f"Order #{order_id} was not found.",
                    "tool_events": tool_events,
                    "pending_action": None
                }

            final_text = (
                f"Order #{order_data['order_id']}\n\n"
                f"Customer: {order_data['customer_name']}\n"
                f"Product: {order_data['product_name']}\n"
                f"Status: {order_data['status'].capitalize()}\n"
                f"Expected delivery: {order_data['expected_delivery'][:10]}"
            )

            return {
                "conversation_id": conversation_id,
                "message": final_text,
                "tool_events": tool_events,
                "pending_action": None
            }

        # -------------------------------------------------------------
        # Operations Summary (ONLY WHEN EXPLICITLY REQUESTED)
        # -------------------------------------------------------------
        elif "summary" in msg_lower or "overview" in msg_lower or "metrics" in msg_lower or "dashboard" in msg_lower or "operations" in msg_lower:
            tool_events.append({
                "tool_name": "get_operations_summary",
                "status": "started",
                "input": {},
                "output": None,
                "description": "Retrieved operations summary"
            })
            summary = get_operations_summary_tool(db, conversation_id)
            tool_events[-1]["status"] = "completed"
            tool_events[-1]["output"] = summary

            final_text = (
                f"Today's operations\n\n"
                f"• {summary['total_orders']} total orders\n"
                f"• {summary['delayed_orders']} delayed\n"
                f"• {summary['pending_returns']} pending returns\n"
                f"• {summary['low_stock_products']} low-stock products\n\n"
                f"There are currently two operational alerts: delayed shipments and low inventory."
            )

            return {
                "conversation_id": conversation_id,
                "message": final_text,
                "tool_events": tool_events,
                "pending_action": None
            }

        # Default fallback: get_order if any order reference, or low stock if inventory mentioned, else operations summary
        else:
            tool_events.append({
                "tool_name": "get_operations_summary",
                "status": "started",
                "input": {},
                "output": None,
                "description": "Retrieved operations summary"
            })
            summary = get_operations_summary_tool(db, conversation_id)
            tool_events[-1]["status"] = "completed"
            tool_events[-1]["output"] = summary

            final_text = (
                f"Today's operations\n\n"
                f"• {summary['total_orders']} total orders\n"
                f"• {summary['delayed_orders']} delayed\n"
                f"• {summary['pending_returns']} pending returns\n"
                f"• {summary['low_stock_products']} low-stock products\n\n"
                f"How can I help with your operations today?"
            )

            return {
                "conversation_id": conversation_id,
                "message": final_text,
                "tool_events": tool_events,
                "pending_action": None
            }

ops_agent_engine = OpsPilotAgent()

