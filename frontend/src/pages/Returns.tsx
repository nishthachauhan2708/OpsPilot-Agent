import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiService } from '../services/api';
import { ReturnRecord } from '../types';
import { RotateCcw, CheckCircle2, Clock, XCircle } from 'lucide-react';

export const Returns: React.FC = () => {
  const [returns, setReturns] = useState<ReturnRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReturns = async () => {
      try {
        const data = await apiService.getReturns();
        setReturns(data);
      } catch (err) {
        console.error('Failed to load returns', err);
      } finally {
        setLoading(false);
      }
    };
    fetchReturns();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto bg-[#0b0f19] text-slate-100 min-h-screen">
      <Header title="Returns" subtitle="Track return requests and claims" />

      <main className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold text-white flex items-center gap-2">
              <RotateCcw className="w-4 h-4 text-sky-400" />
              Return requests ({returns.length})
            </h3>
            <p className="text-xs text-slate-400">All customer return requests</p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 text-xs font-medium">
                <th className="p-4">Return</th>
                <th className="p-4">Order</th>
                <th className="p-4">Reason</th>
                <th className="p-4">Status</th>
                <th className="p-4">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-xs">
              {returns.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4 font-mono font-medium text-sky-400">#RET-{r.id}</td>
                  <td className="p-4 font-mono font-medium text-slate-200">#{r.order_id}</td>
                  <td className="p-4 text-slate-300">{r.reason}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-medium capitalize ${
                      r.status === 'approved' || r.status === 'completed' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20' :
                      r.status === 'pending' ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {r.status}
                    </span>
                  </td>
                  <td className="p-4 text-slate-400">{new Date(r.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
};
