import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiService } from '../services/api';
import { Order } from '../types';
import { Package, Search, Clock, CheckCircle2, Truck, AlertTriangle } from 'lucide-react';

export const Orders: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const data = await apiService.getAllOrders();
        setOrders(data);
      } catch (err) {
        console.error('Failed to load orders', err);
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, []);

  const filteredOrders = orders.filter((o) => {
    const matchesSearch =
      o.id.toString().includes(searchTerm) ||
      (o.customer_name && o.customer_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (o.product_name && o.product_name.toLowerCase().includes(searchTerm.toLowerCase()));
    
    if (filter === 'all') return matchesSearch;
    return matchesSearch && o.status === filter;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-[#0b0f19] text-slate-100 min-h-screen">
      <Header title="Orders" subtitle="Track order status and carrier delivery" />

      <main className="p-6 max-w-7xl mx-auto space-y-5">
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search orders..."
              className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div className="flex items-center gap-2 text-xs">
            {['all', 'delayed', 'shipped', 'processing', 'delivered'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-lg font-medium capitalize transition-colors ${
                  filter === f
                    ? 'bg-sky-600 text-white'
                    : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Orders Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 text-xs font-medium">
                <th className="p-4">Order</th>
                <th className="p-4">Customer</th>
                <th className="p-4">Product</th>
                <th className="p-4">Amount</th>
                <th className="p-4">Status</th>
                <th className="p-4">Delivery</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-xs">
              {filteredOrders.map((o) => (
                <tr key={o.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4 font-mono font-medium text-sky-400">#{o.id}</td>
                  <td className="p-4 font-medium text-white">{o.customer_name}</td>
                  <td className="p-4 text-slate-300">{o.product_name}</td>
                  <td className="p-4 text-slate-200">${o.amount.toFixed(2)}</td>
                  <td className="p-4">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium capitalize ${
                      o.status === 'delayed' ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20' :
                      o.status === 'delivered' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20' :
                      'bg-sky-500/10 text-sky-300 border border-sky-500/20'
                    }`}>
                      {o.status === 'delayed' && <AlertTriangle className="w-3 h-3 text-amber-400" />}
                      {o.status === 'delivered' && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
                      {o.status}
                    </span>
                  </td>
                  <td className="p-4 text-slate-400">
                    {new Date(o.expected_delivery).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
};
