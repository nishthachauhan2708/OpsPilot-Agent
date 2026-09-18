import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Bot,
  ShieldCheck,
  Package,
  Boxes,
  RotateCcw,
  Activity,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { apiService } from '../services/api';

interface SidebarProps {
  pendingActionCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ pendingActionCount }) => {
  const [dbConnected, setDbConnected] = useState<boolean>(false);
  const [aiConnected, setAiConnected] = useState<boolean>(false);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await apiService.getHealth();
        if (res && res.status === 'ok') {
          setDbConnected(true);
          setAiConnected(true);
        }
      } catch (err) {
        setDbConnected(false);
        setAiConnected(false);
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { to: '/', label: 'Overview', icon: LayoutDashboard },
    { to: '/workspace', label: 'Agent Workspace', icon: Bot },
    { to: '/approvals', label: 'Action Approvals', icon: ShieldCheck, badge: pendingActionCount },
    { to: '/orders', label: 'Orders', icon: Package },
    { to: '/inventory', label: 'Inventory', icon: Boxes },
    { to: '/returns', label: 'Returns', icon: RotateCcw },
    { to: '/activity', label: 'Agent Activity', icon: Activity },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between h-screen sticky top-0 select-none">
      <div>
        {/* Logo */}
        <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center shadow-lg shadow-sky-500/20 font-bold text-white text-lg">
            O
          </div>
          <div>
            <h1 className="font-bold text-base text-white tracking-wide flex items-center gap-1.5">
              OpsPilot <span className="text-[10px] px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-400 font-semibold border border-sky-500/20">v1.0</span>
            </h1>
            <p className="text-xs text-slate-400 font-medium">UrbanCart Operations</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs px-2 py-0.5 rounded-full font-semibold">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="p-4 m-3 rounded-lg bg-slate-950 border border-slate-800/80 space-y-2 text-xs">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
          System Connections
        </div>
        <div className="flex items-center justify-between text-slate-300">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Database API
          </span>
          {dbConnected ? (
            <span className="text-emerald-400 font-medium flex items-center gap-1 text-[11px]">
              <CheckCircle2 className="w-3 h-3" /> Connected
            </span>
          ) : (
            <span className="text-rose-400 font-medium flex items-center gap-1 text-[11px]">
              <AlertCircle className="w-3 h-3" /> Offline
            </span>
          )}
        </div>
        <div className="flex items-center justify-between text-slate-300">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse"></span>
            OpsPilot Agent
          </span>
          {aiConnected ? (
            <span className="text-sky-400 font-medium flex items-center gap-1 text-[11px]">
              <CheckCircle2 className="w-3 h-3" /> Ready
            </span>
          ) : (
            <span className="text-rose-400 font-medium flex items-center gap-1 text-[11px]">
              <AlertCircle className="w-3 h-3" /> Standby
            </span>
          )}
        </div>
      </div>
    </aside>
  );
};
