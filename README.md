# OpsPilot - AI Business Operations Agent Platform

**OpsPilot** is an AI-powered internal business operations platform for e-commerce enterprises (demonstrated using synthetic data for fictional retailer **UrbanCart**). Built with FastAPI, SQLite/SQLAlchemy, React, TypeScript, and LangChain, OpsPilot empowers operations teams to investigate orders, customer records, inventory levels, carrier delays, and return eligibility using natural language. It features complete tool execution observability, RAG policy retrieval, and a mandatory **Human-in-the-Loop** approval workflow for write operations that change database state.

---

## Architecture Diagram

```
                              ┌───────────────────────────────────┐
                              │     React + TS Enterprise UI      │
                              └─────────────────┬─────────────────┘
                                                │ REST API
                                                ▼
                              ┌───────────────────────────────────┐
                              │      FastAPI Backend Engine       │
                              └──────┬────────────────────┬───────┘
                                     │                    │
                  ┌──────────────────┴──┐         ┌───────┴────────────────┐
                  │ OpsPilot AI Agent   │         │ SQLite Database        │
                  │  (Tools + RAG Engine)│         │ (Orders, Inventory,    │
                  └──────────┬──────────┘         │ Customers, Returns,    │
                             │                    │ Action Requests, Logs) │
              ┌──────────────┴──────────────┐     └────────────────────────┘
              │                             │
    ┌─────────▼──────────┐       ┌──────────▼─────────┐
    │  9 Domain Tools    │       │  RAG Policy Store  │
    │ (Order, Inventory, │       │ (TF-IDF / Vector   │
    │  Return, Customer) │       │  Search over Docs) │
    └─────────┬──────────┘       └────────────────────┘
              │
              ▼
   ┌──────────────────────┐
   │ Human Approval Queue │
   │ (Write Operations)   │
   └──────────────────────┘
```

---

## Key Features

- 💬 **Natural Language Operations Workspace**: Ask natural language operational questions about orders, inventory, delayed deliveries, and return policies.
- 🛠️ **Real Backend Tool Execution**: 9 specialized backend domain tools retrieve live database records and calculate return eligibility dynamically.
- 📜 **RAG Policy Search**: Grounded policy retrieval across `return_policy.md`, `refund_policy.md`, `shipping_policy.md`, and `customer_support_guidelines.md`.
- 🛡️ **Human-in-the-Loop Security**: Write actions (like creating return requests) generate pending action records. Execution ONLY occurs after explicit human sign-off via `/api/actions/{action_id}/approve`.
- 🔍 **Real-Time Tool Activity Trace**: Live activity step panel displaying tool inputs, outputs, and execution states (`started`, `completed`, `pending_approval`).
- 📊 **Dynamic Operational Dashboard**: Live database metrics for delayed shipments, low stock items, open return claims, and system health status checks.
- 🔒 **Prompt Injection Guardrails**: Built-in guardrail layer filtering prompt injection attempts and system prompt exposure queries.

---

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Axios.
- **Backend**: Python 3.9+, FastAPI, Pydantic V2, SQLAlchemy.
- **Database**: SQLite (SQLAlchemy ORM configured for PostgreSQL migration).
- **AI Agent & RAG**: LangChain tool-based architecture, Gemini / OpenAI LLM integration with deterministic fallback engine, RAG policy retriever.
- **Testing**: Pytest unit & integration test suite.
- **Containerization**: Docker & Docker Compose.

---

## Agent Tools (9 Real Operational Tools)

1. `get_order(order_id)`: Retrieve detailed order and carrier tracking info.
2. `get_customer(customer_id)`: Retrieve customer profile, order history, and open issue count.
3. `get_delayed_orders()`: Retrieve all delayed shipments with carrier status and delay duration.
4. `get_low_stock_products()`: Retrieve inventory items below reorder thresholds with severity badges.
5. `get_return_history(order_id)`: Retrieve past return requests filed for an order.
6. `check_return_eligibility(order_id, reason)`: RAG-backed policy check evaluating delivery dates against standard 7-day or damaged item rules.
7. `create_return_request(order_id, reason)` (*Write Action*): Generates a pending approval record in `action_requests`. Does NOT mutate database until human approves.
8. `draft_customer_message(order_id, issue_type)`: Drafts professional customer update messages incorporating real order data.
9. `get_operations_summary()`: Aggregates real-time business metrics and system operational alerts from database tables.

---

## Database Schema

- `customers`: `id`, `name`, `email`, `created_at`
- `products`: `id`, `name`, `category`, `price`
- `orders`: `id`, `customer_id`, `product_id`, `amount`, `order_date`, `expected_delivery`, `actual_delivery`, `status`, `tracking_status`
- `inventory`: `id`, `product_id`, `stock`, `reorder_level`
- `returns`: `id`, `order_id`, `reason`, `status`, `created_at`, `approved_at`
- `action_requests`: `id`, `action_type`, `payload`, `status`, `created_at`, `reviewed_at`
- `agent_logs`: `id`, `conversation_id`, `tool_name`, `input_summary`, `output_summary`, `status`, `timestamp`

---

## Setup & Running Instructions

### Local Development

#### 1. Backend Setup

```bash
cd opspilot/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt --only-binary :all:

# Seed database
python -m app.database.seed

# Start FastAPI server
python -m app.main
```

Backend will start at: `http://localhost:8000`
Swagger UI API Documentation: `http://localhost:8000/docs`

#### 2. Frontend Setup

```bash
cd opspilot/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at: `http://localhost:5173`

---

### Running with Docker Compose

```bash
cd opspilot
docker compose up --build
```

---

## Running Backend Tests

```bash
cd opspilot/backend
python -m pytest
```

---

## Demonstration Scenarios

1. **Query**: `"Show me today's delayed orders."`  
   *Result*: Agent invokes `get_delayed_orders`, retrieving delayed shipment data including Order #1042.
2. **Query**: `"Which products are currently low on stock?"`  
   *Result*: Agent invokes `get_low_stock_products`, returning stock table with CRITICAL and HIGH severity indicators.
3. **Query**: `"Check order 1042."`  
   *Result*: Agent fetches Order #1042 details and customer info.
4. **Query**: `"Why is order 1042 delayed?"`  
   *Result*: Agent analyzes carrier tracking: *"Delayed at Regional Sorting Hub (Customs inspection clearance pending)"*.
5. **Query**: `"Is order 1042 eligible for a return?"`  
   *Result*: Agent searches RAG policy store (`return_policy.md`) and evaluates order delivery status.
6. **Query**: `"Create a return for order 1042 because the product arrived damaged."`  
   *Result*: Agent generates a **Pending Action Request** card. Clicking **Approve** executes database mutation to create the return.
7. **Dashboard Overview**: Metrics load dynamically from SQLite database APIs.

---

## Synthetic Data Disclaimer

> **Note**: **UrbanCart** is a fictional e-commerce demonstration brand used solely for synthetic data and business scenario testing. All customer names, emails, and order records are synthetic. OpsPilot is designed for deployment across real enterprise retail backend systems.
