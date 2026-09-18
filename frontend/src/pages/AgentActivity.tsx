import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiService } from '../services/api';
import { AgentLog } from '../types';
import { Activity, CheckCircle2, ShieldAlert } from 'lucide-react';

export const AgentActivity: React.FC = () => {
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await apiService.getAgentLogs();
        setLogs(data);
      } catch (err) {
        console.error('Failed to load agent logs', err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto bg-[#0b0f19] text-slate-100 min-h-screen">
      <Header title="Agent Activity" subtitle="Audit log of tool executions" />

      <main className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-sky-400" />
              Activity log ({logs.length})
            </h3>
            <p className="text-xs text-slate-400">Agent tool execution history</p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 text-xs font-medium">
                <th className="p-4">Time</th>
                <th className="p-4">Tool</th>
                <th className="p-4">Status</th>
                <th className="p-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-xs">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4 text-slate-400 text-[11px] font-mono">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="p-4 font-mono font-medium text-sky-400">{log.tool_name}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-medium capitalize ${
                      log.status === 'success' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20' :
                      log.status === 'pending_approval' ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {log.status === 'success' ? 'Completed' : log.status === 'pending_approval' ? 'Pending approval' : log.status}
                    </span>
                  </td>
                  <td className="p-4 text-slate-300 max-w-md truncate" title={log.output_summary}>
                    {log.output_summary}
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
