import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';
import {
  SkeletonRows,
  tableCls, theadCls, thCls, tdCls, trHoverCls,
  inputCls, labelCls,
} from '../components/ui';

const MetricCard = ({ label, value, accent = 'text-white' }) => (
  <div className="bg-kasi-750 rounded-xl p-4 border border-white/[0.04]">
    <p className="text-xs text-slate-500 mb-1.5">{label}</p>
    <p className={`text-xl font-bold ${accent}`}>{value}</p>
  </div>
);

const Reports = () => {
  const [revenueBreakdown, setRevenueBreakdown] = useState([]);
  const [userEngagement, setUserEngagement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => { loadData(); }, [dateFrom, dateTo]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [revenue, engagement] = await Promise.all([
        analyticsService.getRevenueBreakdown(dateFrom || null, dateTo || null),
        analyticsService.getUserEngagement(),
      ]);
      setRevenueBreakdown(revenue || []);
      setUserEngagement(engagement);
    } catch (err) {
      console.error('Failed to load reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const fmtR = (n) => `R ${Number(n || 0).toFixed(2)}`;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Analytics & Reports</h1>

      {/* Date filters */}
      <div className="bg-kasi-800 border border-white/[0.05] rounded-xl p-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>From Date</label>
            <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} className={inputCls} />
          </div>
          <div>
            <label className={labelCls}>To Date</label>
            <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} className={inputCls} />
          </div>
        </div>
      </div>

      {/* User Engagement */}
      {userEngagement && (
        <div className="bg-kasi-800 border border-white/[0.05] rounded-xl p-5">
          <h2 className="text-base font-semibold text-white mb-4">User Engagement</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <MetricCard label="Total Users"       value={userEngagement.total_users.toLocaleString()} />
            <MetricCard label="Active (24h)"      value={userEngagement.active_users_24h.toLocaleString()}  accent="text-blue-400" />
            <MetricCard label="Active (7d)"       value={userEngagement.active_users_7d.toLocaleString()}   accent="text-blue-400" />
            <MetricCard label="Active (30d)"      value={userEngagement.active_users_30d.toLocaleString()}  accent="text-blue-400" />
            <MetricCard label="New Today"         value={userEngagement.new_users_today.toLocaleString()}   accent="text-emerald-400" />
            <MetricCard label="New (7d)"          value={userEngagement.new_users_7d.toLocaleString()}      accent="text-emerald-400" />
            <MetricCard label="Avg Bets / User"   value={userEngagement.average_bets_per_user.toFixed(1)}  accent="text-purple-400" />
            <MetricCard label="Avg Deposit / User" value={fmtR(userEngagement.average_deposit_per_user)}   accent="text-amber-400" />
          </div>
        </div>
      )}

      {/* Revenue Breakdown */}
      <div className={tableCls}>
        <div className="px-6 py-4 border-b border-white/[0.05]">
          <h2 className="text-base font-semibold text-white">Revenue Breakdown by Game Type</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className={theadCls}>
              <tr>
                <th className={thCls}>Game Type</th>
                <th className={thCls}>Total Wagered</th>
                <th className={thCls}>Total Payouts</th>
                <th className={thCls}>Net Revenue</th>
                <th className={thCls}>Bet Count</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <SkeletonRows cols={5} rows={4} />
              ) : revenueBreakdown.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-14 text-center text-slate-500 text-sm">No data for selected period</td>
                </tr>
              ) : (
                revenueBreakdown.map((item) => (
                  <tr key={item.game_type} className={trHoverCls}>
                    <td className={`${tdCls} font-medium text-white capitalize`}>{item.game_type}</td>
                    <td className={`${tdCls} text-amber-400`}>{fmtR(item.total_wagered)}</td>
                    <td className={`${tdCls} text-slate-400`}>{fmtR(item.total_payouts)}</td>
                    <td className={`${tdCls} font-semibold ${item.net_revenue >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {fmtR(item.net_revenue)}
                    </td>
                    <td className={tdCls}>{item.bet_count.toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Reports;
