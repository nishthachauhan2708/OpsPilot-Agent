import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { PendingActionCard } from '../components/PendingActionCard';
import { apiService } from '../services/api';
import { ActionRequest } from '../types';
import { ShieldCheck, RefreshCw, CheckCircle } from 'lucide-react';

export const ActionApprovals: React.FC = () => {
  const [actions, setActions] = useState<ActionRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPendingActions = async () => {
    setLoading(true);
    try {
      const data = await apiService.getPendingActions();
      setActions(data);
    } catch (err) {
      console.error('Failed to load pending actions', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingActions();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto bg-[#0b0f19] text-slate-100 min-h-screen">
      <Header title="Action Approvals" subtitle="Review proposed write actions" />

      <main className="p-6 max-w-5xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-amber-400" />
              Pending actions ({actions.length})
            </h3>
            <p className="text-xs text-slate-400">
              Actions prepared by OpsPilot awaiting approval
            </p>
          </div>
          <button
            onClick={fetchPendingActions}
            className="p-2 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 rounded-lg text-xs flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {actions.length === 0 && !loading && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center space-y-3">
            <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto" />
            <h4 className="text-xs font-semibold text-slate-200">No pending approvals</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              All proposed return requests have been reviewed.
            </p>
          </div>
        )}

        <div className="space-y-4">
          {actions.map((act) => (
            <PendingActionCard
              key={act.id}
              action={act}
              onActionComplete={fetchPendingActions}
            />
          ))}
        </div>
      </main>
    </div>
  );
};
