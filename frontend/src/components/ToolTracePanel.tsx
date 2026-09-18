import React from 'react';
import { ToolEvent } from '../types';
import { CheckCircle2, Clock, AlertTriangle, ShieldAlert } from 'lucide-react';

interface ToolTracePanelProps {
  toolEvents: ToolEvent[];
  isThinking: boolean;
}

export const ToolTracePanel: React.FC<ToolTracePanelProps> = ({ toolEvents, isThinking }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-sky-400"></span>
          Backend Tool Trace
        </h3>
        <span className="text-[11px] text-slate-400 font-mono">
          {toolEvents.length} event(s)
        </span>
      </div>

      {isThinking && toolEvents.length === 0 && (
        <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-xs text-sky-400 flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 animate-spin" />
          <span>Selecting tool...</span>
        </div>
      )}

      {toolEvents.length === 0 && !isThinking && (
        <div className="text-xs text-slate-500 py-6 text-center italic">
          No tool execution trace yet.
        </div>
      )}

      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
        {toolEvents.map((evt, idx) => (
          <div key={idx} className="p-3 bg-slate-950/90 border border-slate-800/80 rounded-lg space-y-1 text-xs">
            <div className="flex items-center justify-between font-mono">
              <span className="font-medium text-sky-400 flex items-center gap-1.5">
                {evt.status === 'completed' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                {evt.status === 'started' && <Clock className="w-3.5 h-3.5 text-amber-400 animate-spin" />}
                {evt.status === 'pending_approval' && <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />}
                {evt.status === 'failed' && <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />}
                {evt.tool_name}
              </span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                evt.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                evt.status === 'pending_approval' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                'bg-slate-800 text-slate-400'
              }`}>
                {evt.status === 'completed' ? 'Completed' : evt.status === 'pending_approval' ? 'Waiting for approval' : evt.status}
              </span>
            </div>

            <p className="text-[11px] text-slate-300">
              {evt.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
