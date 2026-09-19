import React, { useState } from 'react';
import { apiService } from '../services/api';
import { ImportResult } from '../types';
import {
  Upload,
  Download,
  FileText,
  CheckCircle2,
  AlertCircle,
  Package,
  Boxes,
  RotateCcw,
  Users,
  HelpCircle,
  Loader2
} from 'lucide-react';

interface CompanyDataImportProps {
  onImportSuccess?: () => void;
}

type ImportCategory = 'orders' | 'inventory' | 'returns' | 'customers' | 'customer-issues';

interface CategoryConfig {
  id: ImportCategory;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  acceptedFormat: string;
}

const CATEGORIES: CategoryConfig[] = [
  {
    id: 'orders',
    name: 'Orders',
    description: 'Upload order tracking data, status updates, carrier details, and fulfillment timestamps.',
    icon: Package,
    acceptedFormat: '.csv, .xlsx'
  },
  {
    id: 'inventory',
    name: 'Inventory',
    description: 'Update stock levels, reorder thresholds, pricing, and product catalog metadata.',
    icon: Boxes,
    acceptedFormat: '.csv, .xlsx'
  },
  {
    id: 'returns',
    name: 'Returns',
    description: 'Import return requests, return reasons, approval dates, and resolution statuses.',
    icon: RotateCcw,
    acceptedFormat: '.csv, .xlsx'
  },
  {
    id: 'customers',
    name: 'Customers',
    description: 'Update customer contact profiles, email addresses, and account registration dates.',
    icon: Users,
    acceptedFormat: '.csv, .xlsx'
  },
  {
    id: 'customer-issues',
    name: 'Customer Issues',
    description: 'Track open customer inquiries, delayed shipment complaints, and resolution logs.',
    icon: HelpCircle,
    acceptedFormat: '.csv, .xlsx'
  }
];

export const CompanyDataImport: React.FC<CompanyDataImportProps> = ({ onImportSuccess }) => {
  const [activeCategory, setActiveCategory] = useState<ImportCategory>('orders');
  const [selectedFiles, setSelectedFiles] = useState<Record<string, File | null>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  const [results, setResults] = useState<Record<string, ImportResult | null>>({});
  const [errorMsgs, setErrorMsgs] = useState<Record<string, string | null>>({});

  const handleFileChange = (catId: ImportCategory, file: File | null) => {
    setSelectedFiles((prev) => ({ ...prev, [catId]: file }));
    setErrorMsgs((prev) => ({ ...prev, [catId]: null }));
  };

  const handleUpload = async (catId: ImportCategory) => {
    const file = selectedFiles[catId];
    if (!file) {
      setErrorMsgs((prev) => ({ ...prev, [catId]: 'Please select a CSV file to upload.' }));
      return;
    }

    setLoading((prev) => ({ ...prev, [catId]: true }));
    setErrorMsgs((prev) => ({ ...prev, [catId]: null }));
    setResults((prev) => ({ ...prev, [catId]: null }));

    try {
      const res = await apiService.importData(catId, file);
      setResults((prev) => ({ ...prev, [catId]: res }));
      if (res.success && onImportSuccess) {
        onImportSuccess();
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to import CSV data.';
      setErrorMsgs((prev) => ({ ...prev, [catId]: msg }));
    } finally {
      setLoading((prev) => ({ ...prev, [catId]: false }));
    }
  };

  const handleDownloadTemplate = (catId: ImportCategory) => {
    const url = apiService.getTemplateUrl(catId);
    window.open(url, '_blank');
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Upload className="w-5 h-5 text-sky-400" />
            Company Data Import
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Upload your business data to update orders, inventory, returns, customer records and issues.
          </p>
        </div>
        <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 text-xs text-slate-400">
          <FileText className="w-4 h-4 text-sky-400" />
          <span>Supports CSV & Excel format</span>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        {CATEGORIES.map((cat) => {
          const Icon = cat.icon;
          const isActive = activeCategory === cat.id;
          const hasResult = results[cat.id]?.success;
          return (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`flex flex-col items-center justify-center p-3 rounded-xl border text-xs font-medium transition-all ${
                isActive
                  ? 'bg-sky-500/10 border-sky-500/40 text-sky-300 shadow-sm'
                  : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-1.5 mb-1">
                <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                {hasResult && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
              </div>
              <span className="font-semibold">{cat.name}</span>
            </button>
          );
        })}
      </div>

      {/* Active Category Import Card */}
      {CATEGORIES.filter((c) => c.id === activeCategory).map((cat) => {
        const Icon = cat.icon;
        const file = selectedFiles[cat.id];
        const isUploading = loading[cat.id];
        const res = results[cat.id];
        const err = errorMsgs[cat.id];

        return (
          <div key={cat.id} className="bg-slate-950/80 border border-slate-800/90 rounded-xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-sky-500/10 border border-sky-500/20 flex items-center justify-center shrink-0">
                  <Icon className="w-5 h-5 text-sky-400" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{cat.name} Import</h3>
                  <p className="text-xs text-slate-400">{cat.description}</p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => handleDownloadTemplate(cat.id)}
                className="inline-flex items-center gap-1.5 text-xs font-medium text-sky-400 hover:text-sky-300 bg-slate-900 border border-slate-800 hover:border-slate-700 px-3 py-1.5 rounded-lg transition-colors shrink-0"
              >
                <Download className="w-3.5 h-3.5" />
                Download {cat.name} Template
              </button>
            </div>

            {/* Upload Controls */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-slate-300 mb-1.5">
                  Select CSV File ({cat.acceptedFormat})
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="file"
                    accept=".csv, .txt, .xlsx"
                    onChange={(e) => handleFileChange(cat.id, e.target.files?.[0] || null)}
                    className="block w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 cursor-pointer bg-slate-900 border border-slate-800 rounded-lg"
                  />
                </div>
              </div>

              <div className="flex items-end">
                <button
                  type="button"
                  disabled={!file || isUploading}
                  onClick={() => handleUpload(cat.id)}
                  className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-semibold text-xs transition-all ${
                    !file || isUploading
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      : 'bg-sky-600 hover:bg-sky-500 text-white shadow-md shadow-sky-600/20'
                  }`}
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-white" />
                      Uploading & Processing...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Upload & Import {cat.name}
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Error Banner */}
            {err && (
              <div className="p-3 bg-rose-950/30 border border-rose-500/30 rounded-lg flex items-start gap-2.5 text-xs text-rose-300">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold">Import Error: </span>
                  {err}
                </div>
              </div>
            )}

            {/* Success Result Box */}
            {res && res.success && (
              <div className="p-4 bg-emerald-950/20 border border-emerald-500/30 rounded-lg space-y-2 text-xs">
                <div className="flex items-center gap-2 text-emerald-400 font-semibold text-sm">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  Import Complete & Database Updated
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 text-slate-300">
                  <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                    <span className="text-slate-500 text-[11px] block">File Status</span>
                    <span className="text-emerald-400 font-medium">✓ File Validated</span>
                  </div>
                  <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                    <span className="text-slate-500 text-[11px] block">New Records</span>
                    <span className="text-white font-semibold">{res.imported} imported</span>
                  </div>
                  <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                    <span className="text-slate-500 text-[11px] block">Updated Records</span>
                    <span className="text-sky-300 font-semibold">{res.updated} updated</span>
                  </div>
                  <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                    <span className="text-slate-500 text-[11px] block">Skipped / Errors</span>
                    <span className={res.skipped > 0 ? 'text-amber-400 font-semibold' : 'text-slate-400'}>
                      {res.skipped} skipped
                    </span>
                  </div>
                </div>

                {res.errors && res.errors.length > 0 && (
                  <div className="mt-2 p-2 bg-slate-900 rounded border border-amber-500/20 text-[11px] text-amber-300 space-y-1 max-h-32 overflow-y-auto">
                    <div className="font-semibold">Row Warnings ({res.errors.length}):</div>
                    {res.errors.map((e, idx) => (
                      <div key={idx}>• {e}</div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
