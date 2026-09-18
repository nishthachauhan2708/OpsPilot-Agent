import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { AgentWorkspace } from './pages/AgentWorkspace';
import { ActionApprovals } from './pages/ActionApprovals';
import { Orders } from './pages/Orders';
import { Inventory } from './pages/Inventory';
import { Returns } from './pages/Returns';
import { AgentActivity } from './pages/AgentActivity';
import { apiService } from './services/api';

export const App: React.FC = () => {
  const [pendingActionCount, setPendingActionCount] = useState<number>(0);

  const updatePendingCount = async () => {
    try {
      const actions = await apiService.getPendingActions();
      setPendingActionCount(actions.length);
    } catch (err) {
      // Quiet fail if API starting up
    }
  };

  useEffect(() => {
    updatePendingCount();
    const interval = setInterval(updatePendingCount, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
      <div className="flex h-screen bg-slate-950 text-slate-100 font-sans overflow-hidden">
        <Sidebar pendingActionCount={pendingActionCount} />
        
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/workspace" element={<AgentWorkspace onActionCreated={updatePendingCount} />} />
            <Route path="/approvals" element={<ActionApprovals />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/returns" element={<Returns />} />
            <Route path="/activity" element={<AgentActivity />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;
