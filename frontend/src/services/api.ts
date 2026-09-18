import axios from 'axios';
import {
  Order,
  InventoryItem,
  ReturnRecord,
  ActionRequest,
  AgentLog,
  AnalyticsSummary,
  AgentChatResponse
} from '../types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  getHealth: async () => {
    const res = await api.get('/health');
    return res.data;
  },

  getAnalyticsSummary: async (): Promise<AnalyticsSummary> => {
    const res = await api.get('/analytics/summary');
    return res.data;
  },

  getDelayedOrders: async (): Promise<Order[]> => {
    const res = await api.get('/orders/delayed');
    return res.data;
  },

  getOrder: async (orderId: number): Promise<Order> => {
    const res = await api.get(`/orders/${orderId}`);
    return res.data;
  },

  getLowStockInventory: async (): Promise<InventoryItem[]> => {
    const res = await api.get('/inventory/low-stock');
    return res.data;
  },

  getReturns: async (): Promise<ReturnRecord[]> => {
    const res = await api.get('/returns');
    return res.data;
  },

  getPendingActions: async (): Promise<ActionRequest[]> => {
    const res = await api.get('/actions/pending');
    return res.data;
  },

  approveAction: async (actionId: number): Promise<ActionRequest> => {
    const res = await api.post(`/actions/${actionId}/approve`);
    return res.data;
  },

  rejectAction: async (actionId: number): Promise<ActionRequest> => {
    const res = await api.post(`/actions/${actionId}/reject`);
    return res.data;
  },

  sendAgentMessage: async (message: string, conversationId: string = 'ops-session-001'): Promise<AgentChatResponse> => {
    const res = await api.post('/agent/chat', {
      message,
      conversation_id: conversationId,
    });
    return res.data;
  },

  getAgentLogs: async (): Promise<AgentLog[]> => {
    const res = await api.get('/agent/logs');
    return res.data;
  },
};
