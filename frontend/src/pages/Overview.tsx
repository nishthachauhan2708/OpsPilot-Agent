import React, { useEffect, useState, useCallback } from 'react';
import { Header } from '../components/Header';
import { CompanyDataImport } from '../components/CompanyDataImport';
import { apiService } from '../services/api';
import { AnalyticsSummary, AgentLog } from '../types';
import {
  Package,
  Clock,
  RotateCcw,
  AlertTriangle,
  ShieldAlert,
  ArrowUpRight,
  Activity,
  HelpCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const Overview: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [sumRes, logsRes] = await Promise.all([
        apiService.getAnalyticsSummary(),
        apiService.getAgentLogs()
      ]);
      setSummary(sumRes);
      setLogs(logsRes.slice(0, 5));
    } catch (err) {
      console.error('Failed to load summary data', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="flex-1 overflow-y-auto bg-[#0b0f19] text-slate-100 min-h-screen">
      <Header title="Overview" subtitle="UrbanCart operational metrics and company data management" />

      <main className="p-6 space-y-6 max-w-7xl mx-auto">
        {/* Top Operational Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-1.5">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium text-slate-400">Total orders</span>
              <Package className="w-4 h-4 text-sky-400" />
            </div>
            <div className="text-2xl font-semibold text-white">
              {loading ? '...' : summary?.total_orders}
            </div>
            <p className="text-[11px] text-slate-500">Tracked orders</p>
          </div>

          <div className="bg-slate-900/90 border border-amber-500/20 rounded-xl p-4 space-y-1.5">
            <div className="flex items-center justify-between text-amber-300">
              <span className="text-xs font-medium text-slate-400">Delayed orders</span>
              <Clock className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-semibold text-amber-300">
              {loading ? '...' : summary?.delayed_orders}
            </div>
            <Link to="/orders" className="text-[11px] text-amber-400/80 hover:text-amber-300 flex items-center gap-1 font-medium">
              Currently delayed <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-1.5">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium text-slate-400">Pending returns</span>
              <RotateCcw className="w-4 h-4 text-sky-400" />
            </div>
            <div className="text-2xl font-semibold text-white">
              {loading ? '...' : summary?.pending_returns}
            </div>
            <Link to="/returns" className="text-[11px] text-sky-400 hover:underline flex items-center gap-1 font-medium">
              Awaiting review <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="bg-slate-900/90 border border-rose-500/20 rounded-xl p-4 space-y-1.5">
            <div className="flex items-center justify-between text-rose-400">
              <span className="text-xs font-medium text-slate-400">Low stock</span>
              <AlertTriangle className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-2xl font-semibold text-rose-300">
              {loading ? '...' : summary?.low_stock_products}
            </div>
            <Link to="/inventory" className="text-[11px] text-rose-400/80 hover:text-rose-300 flex items-center gap-1 font-medium">
              Below reorder level <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="bg-slate-900/90 border border-purple-500/20 rounded-xl p-4 space-y-1.5">
            <div className="flex items-center justify-between text-purple-300">
              <span className="text-xs font-medium text-slate-400">Open issues</span>
              <HelpCircle className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-semibold text-purple-300">
              {loading ? '...' : summary?.open_customer_issues}
            </div>
            <span className="text-[11px] text-purple-400/80 font-medium">
              Customer tickets
            </span>
          </div>
        </div>

        {/* Action Required Banner if pending approval */}
        {(summary?.pending_actions_count || 0) > 0 && (
          <div className="bg-slate-900 border border-amber-500/30 rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0" />
              <div>
                <h4 className="text-xs font-semibold text-amber-300">
                  {summary?.pending_actions_count} action(s) awaiting approval
                </h4>
                <p className="text-xs text-slate-400">
                  Review proposed return requests before applying changes.
                </p>
              </div>
            </div>
            <Link
              to="/approvals"
              className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold text-xs px-3.5 py-1.5 rounded-lg transition-colors"
            >
              Review approvals
            </Link>
          </div>
        )}

        {/* Company Data Import Section */}
        <CompanyDataImport onImportSuccess={fetchData} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Operational Alerts */}
          <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
            <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              Operational alerts
            </h3>

            <div className="space-y-3">
              {summary?.recent_alerts.map((alert, idx) => (
                <div
                  key={idx}
                  className={`p-3.5 rounded-lg border flex items-start gap-3 ${
                    alert.type === 'critical'
                      ? 'bg-rose-950/20 border-rose-500/20 text-rose-200'
                      : alert.type === 'warning'
                      ? 'bg-amber-950/20 border-amber-500/20 text-amber-200'
                      : 'bg-slate-800/40 border-slate-700/50 text-slate-200'
                  }`}
                >
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  <div>
                    <h5 className="font-semibold text-xs">{alert.title}</h5>
                    <p className="text-xs mt-0.5 text-slate-300">{alert.message}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Agent Activity */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-3.5 h-3.5 text-sky-400" />
                Recent activity
              </h3>
              <Link to="/activity" className="text-xs text-sky-400 hover:underline">
                View all
              </Link>
            </div>

            <div className="space-y-2.5">
              {logs.map((log) => (
                <div key={log.id} className="p-3 bg-slate-950/80 rounded-lg border border-slate-800/80 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sky-400 font-medium">{log.tool_name}</span>
                    <span className="text-[10px] text-slate-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <p className="text-slate-400 text-[11px] line-clamp-1">{log.output_summary}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
