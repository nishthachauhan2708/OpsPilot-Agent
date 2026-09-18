import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiService } from '../services/api';
import { InventoryItem } from '../types';
import { Boxes, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const Inventory: React.FC = () => {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInventory = async () => {
      try {
        const data = await apiService.getLowStockInventory();
        setInventory(data);
      } catch (err) {
        console.error('Failed to load inventory', err);
      } finally {
        setLoading(false);
      }
    };
    fetchInventory();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto bg-[#0b0f19] text-slate-100 min-h-screen">
      <Header title="Inventory" subtitle="Monitor product stock and reorder levels" />

      <main className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-semibold text-white flex items-center gap-2">
              <Boxes className="w-4 h-4 text-rose-400" />
              Low stock items ({inventory.length})
            </h3>
            <p className="text-xs text-slate-400">Products at or below reorder level</p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 text-xs font-medium">
                <th className="p-4">Product</th>
                <th className="p-4">Category</th>
                <th className="p-4">Stock</th>
                <th className="p-4">Reorder level</th>
                <th className="p-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 text-xs">
              {inventory.map((item) => {
                const isLow = item.stock <= item.reorder_level;
                const isCritical = item.stock <= 2;
                return (
                  <tr key={item.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-4 font-medium text-white">{item.product_name}</td>
                    <td className="p-4 text-slate-400">Electronics</td>
                    <td className="p-4">
                      <span className={`font-medium ${isCritical ? 'text-rose-400' : 'text-amber-300'}`}>
                        {item.stock}
                      </span>
                    </td>
                    <td className="p-4 text-slate-400">{item.reorder_level}</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-medium ${
                        isCritical ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20' : 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                      }`}>
                        {isCritical ? 'Critical' : 'Low stock'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
};
