import React, { useState } from 'react';
import { ActionRequest } from '../types';
import { ShieldAlert, CheckCircle2, XCircle, ArrowRight } from 'lucide-react';
import { apiService } from '../services/api';

interface PendingActionCardProps {
  action: ActionRequest;
  onActionComplete?: () => void;
}

export const PendingActionCard: React.FC<PendingActionCardProps> = ({ action, onActionComplete }) => {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'pending' | 'approved' | 'rejected'>(action.status);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleApprove = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      await apiService.approveAction(action.id);
      setStatus('approved');
      if (onActionComplete) onActionComplete();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to approve action');
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      await apiService.rejectAction(action.id);
      setStatus('rejected');
      if (onActionComplete) onActionComplete();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to reject action');
    } finally {
      setLoading(false);
    }
  };

  const payload = action.payload || {};

  return (
    <div className="bg-slate-900 border border-amber-500/30 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2 text-amber-300 font-semibold text-sm">
          <ShieldAlert className="w-4 h-4 text-amber-400" />
          <span>Return request</span>
        </div>
        <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
          status === 'pending' ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20' :
          status === 'approved' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20' :
          'bg-rose-500/10 text-rose-300 border border-rose-500/20'
        }`}>
          {status === 'pending' ? 'Pending approval' : status === 'approved' ? 'Approved' : 'Rejected'}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs bg-slate-950/80 p-3.5 rounded-lg border border-slate-800">
        <div>
          <span className="text-slate-400">Order:</span>
          <span className="font-semibold text-white ml-2">#{payload.order_id || 'N/A'}</span>
        </div>
        <div>
          <span className="text-slate-400">Customer:</span>
          <span className="font-semibold text-white ml-2">{payload.customer_name || 'N/A'}</span>
        </div>
        <div className="sm:col-span-2">
          <span className="text-slate-400">Reason:</span>
          <span className="font-medium text-slate-200 ml-2">{payload.reason || 'N/A'}</span>
        </div>
      </div>

      <p className="text-xs text-slate-400">
        OpsPilot has prepared this action. No database change has been made yet.
      </p>

      {errorMsg && (
        <div className="p-2.5 bg-rose-500/10 border border-rose-500/30 rounded text-rose-400 text-xs">
          {errorMsg}
        </div>
      )}

      {status === 'pending' ? (
        <div className="flex items-center gap-3 pt-1">
          <button
            onClick={handleApprove}
            disabled={loading}
            className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Approve</span>
          </button>
          <button
            onClick={handleReject}
            disabled={loading}
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 font-medium text-xs py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            <XCircle className="w-4 h-4" />
            <span>Reject</span>
          </button>
        </div>
      ) : status === 'approved' ? (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-300 text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Return request created successfully.</span>
        </div>
      ) : (
        <div className="p-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 text-xs font-medium flex items-center gap-2">
          <XCircle className="w-4 h-4 text-slate-400" />
          <span>Return request rejected.</span>
        </div>
      )}
    </div>
  );
};
