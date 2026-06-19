import React from 'react';
import { Download, FileSpreadsheet, FileText } from 'lucide-react';
import { exportPortfolioCsv } from '../../api';
import { PortfolioAnalytics } from '../../types';
import { fmt } from '../../utils';

interface Props { analytics: PortfolioAnalytics | null }

export const PortfolioExport: React.FC<Props> = ({ analytics }) => {
  const exportCsv = () => {
    window.open(exportPortfolioCsv(), '_blank');
  };

  const exportExcel = () => {
    // CSV opens in Excel
    exportCsv();
  };

  const exportPdf = () => {
    const w = window.open('', '_blank');
    if (!w || !analytics) return;
    w.document.write(`<!DOCTYPE html><html><head><title>AcquiSight Pipeline Report</title>
      <style>body{font-family:Arial,sans-serif;padding:40px;color:#111}
      h1{color:#1a5f6b}table{border-collapse:collapse;width:100%;margin-top:20px}
      th,td{border:1px solid #ddd;padding:8px;text-align:left}th{background:#f5f5f5}</style></head><body>
      <h1>AcquiSight AI — Investment Pipeline Report</h1>
      <p>Generated ${new Date().toLocaleString()}</p>
      <h2>Portfolio Summary</h2>
      <ul>
        <li>Total Opportunities: ${analytics.total_opportunities}</li>
        <li>Average Investment Score: ${analytics.avg_investment_score}</li>
        <li>Average Risk Score: ${analytics.avg_risk_score}</li>
        <li>Total Enterprise Value: ${fmt.usdM(analytics.total_enterprise_value)}</li>
      </ul>
      <p><em>Full rankings and charts available in Portfolio Mode.</em></p>
      <script>window.print()</script></body></html>`);
    w.document.close();
  };

  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-slate-200 mb-3">Export Pipeline</h3>
      <div className="flex flex-wrap gap-2">
        <button type="button" className="btn-ghost text-xs" onClick={exportCsv}>
          <Download size={14} /> CSV
        </button>
        <button type="button" className="btn-ghost text-xs" onClick={exportExcel}>
          <FileSpreadsheet size={14} /> Excel
        </button>
        <button type="button" className="btn-ghost text-xs" onClick={exportPdf} disabled={!analytics}>
          <FileText size={14} /> PDF Report
        </button>
      </div>
    </div>
  );
};
