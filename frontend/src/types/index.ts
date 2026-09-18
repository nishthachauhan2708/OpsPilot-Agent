export interface Order {
  id: number;
  customer_id: number;
  product_id: number;
  amount: number;
  order_date: string;
  expected_delivery: string;
  actual_delivery?: string | null;
  status: string;
  tracking_status: string;
  customer_name?: string;
  product_name?: string;
}

export interface InventoryItem {
  id: number;
  product_id: number;
  product_name: string;
  stock: number;
  reorder_level: number;
  is_low_stock: boolean;
}

export interface ReturnRecord {
  id: number;
  order_id: number;
  reason: string;
  status: string;
  created_at: string;
  approved_at?: string | null;
  customer_name?: string;
  product_name?: string;
}

export interface ActionRequest {
  id: number;
  action_type: string;
  payload: Record<string, any>;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  reviewed_at?: string | null;
}

export interface AgentLog {
  id: number;
  conversation_id: string;
  tool_name: string;
  input_summary: string;
  output_summary: string;
  status: string;
  timestamp: string;
}

export interface AnalyticsSummary {
  total_orders: number;
  delayed_orders: number;
  pending_returns: number;
  low_stock_products: number;
  open_customer_issues: number;
  pending_actions_count?: number;
  recent_alerts: Array<{
    type: string;
    title: string;
    message: string;
  }>;
}

export interface ToolEvent {
  tool_name: string;
  status: 'started' | 'completed' | 'failed' | 'pending_approval';
  input: Record<string, any>;
  output: any;
  description: string;
}

export interface AgentChatResponse {
  conversation_id: string;
  message: string;
  tool_events: ToolEvent[];
  pending_action?: ActionRequest | null;
}
