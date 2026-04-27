import React, { useState, useEffect } from 'react';
import { betService } from '../services/betService';
import toast from 'react-hot-toast';
import {
  Icon, Badge, SkeletonRows,
  tableCls, theadCls, thCls, tdCls, trHoverCls,
  selectCls, labelCls, inputCls, btnPrimary,
} from '../components/ui';

const Bets = () => {
  const [bets, setBets] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({ bet_type: '', status: '', date_from: '', date_to: '' });

  useEffect(() => { loadBets(); loadStatistics(); }, [page, filters]);

  const activeFilters = () => {
    const f = {};
    if (filters.bet_type) f.bet_type = filters.bet_type;
    if (filters.status)   f.status   = filters.status;
    if (filters.date_from) f.date_from = filters.date_from;
    if (filters.date_to)   f.date_to   = filters.date_to;
    return f;
  };

  const loadBets = async () => {
    setLoading(true);
    try {
      const data = await betService.getBets(page, pageSize, activeFilters());
      setBets(data.bets || []);
      setTotal(data.total || 0);
    } catch {
      toast.error('Failed to load bets');
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const af = activeFilters();
      const data = await betService.getBetStatistics({ bet_type: af.bet_type, date_from: af.date_from, date_to: af.date_to });
      setStatistics(data);
    } catch (err) {
      console.error('Failed to load bet statistics:', err);
    }
  };

  const exportToCSV = () => {
    const headers = ['ID', 'User', 'Bet Type', 'Stake', 'Status', 'Payout', 'Created'];
    const rows = bets.map((b) => [b.id, b.user_phone, b.bet_type, b.stake_amount, b.status, b.payout_amount, b.created_at]);
    const csv = [headers, ...rows].map((r) => r.join(',')).join('\n');
    const a = Object.assign(document.createElement('a'), {
      href: URL.createObjectURL(new Blob([csv], { type: 'text/csv' })),
      download: `bets-${new Date().toISOString()}.csv`,
    });
    a.click();
  };

  const setFilter = (key, val) => { setFilters((f) => ({ ...f, [key]: val })); setPage(1); };
  const fmtR = (n) => `R ${Number(n || 0).toFixed(2)}`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Bets</h1>
        <button onClick={exportToCSV} className={btnPrimary}>
          <Icon name="download" className="w-4 h-4" />
          Export CSV
        </button>
      </div>

      {/* Stats row */}
      {statistics && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Total Bets',   value: statistics.total_bets,                       color: 'text-white' },
            { label: 'Active Bets',  value: statistics.active_bets,                      color: 'text-blue-400' },
            { label: 'Total Wagered',value: fmtR(statistics.total_wagered),              color: 'text-amber-400' },
            { label: 'Net Revenue',  value: fmtR(statistics.net_revenue),                color: statistics.net_revenue >= 0 ? 'text-emerald-400' : 'text-red-400' },
          ].map(({ label, value, color }) => (
            <div key={label} className="bg-kasi-800 border border-white/[0.05] rounded-xl p-4">
              <p className="text-xs text-slate-500 mb-1.5">{label}</p>
              <p className={`text-xl font-bold ${color}`}>{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="bg-kasi-800 border border-white/[0.05] rounded-xl p-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className={labelCls}>Bet Type</label>
            <select value={filters.bet_type} onChange={(e) => setFilter('bet_type', e.target.value)} className={selectCls}>
              <option value="">All Types</option>
              <option value="lucky_wheel">Lucky Wheel</option>
              <option value="color_game">Color Game</option>
              <option value="pick_3">Pick 3</option>
              <option value="football_yesno">Football Yes/No</option>
            </select>
          </div>
          <div>
            <label className={labelCls}>Status</label>
            <select value={filters.status} onChange={(e) => setFilter('status', e.target.value)} className={selectCls}>
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="won">Won</option>
              <option value="lost">Lost</option>
            </select>
          </div>
          <div>
            <label className={labelCls}>From Date</label>
            <input type="date" value={filters.date_from} onChange={(e) => setFilter('date_from', e.target.value)} className={inputCls} />
          </div>
          <div>
            <label className={labelCls}>To Date</label>
            <input type="date" value={filters.date_to} onChange={(e) => setFilter('date_to', e.target.value)} className={inputCls} />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className={tableCls}>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className={theadCls}>
              <tr>
                <th className={thCls}>ID</th>
                <th className={thCls}>User</th>
                <th className={thCls}>Type</th>
                <th className={thCls}>Stake</th>
                <th className={thCls}>Status</th>
                <th className={thCls}>Payout</th>
                <th className={thCls}>Created</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <SkeletonRows cols={7} rows={8} />
              ) : bets.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-14 text-center text-slate-500 text-sm">
                    No bets found
                  </td>
                </tr>
              ) : (
                bets.map((bet) => (
                  <tr key={bet.id} className={trHoverCls}>
                    <td className={`${tdCls} font-mono text-xs text-slate-500`}>{bet.id}</td>
                    <td className={tdCls}>{bet.user_phone}</td>
                    <td className={tdCls}>
                      <span className="text-xs bg-kasi-750 border border-white/[0.06] px-2 py-0.5 rounded-md text-slate-300">
                        {bet.bet_type}
                      </span>
                    </td>
                    <td className={`${tdCls} text-amber-400 font-medium`}>{fmtR(bet.stake_amount)}</td>
                    <td className={tdCls}><Badge status={bet.status} /></td>
                    <td className={`${tdCls} ${bet.payout_amount > 0 ? 'text-emerald-400' : 'text-slate-400'} font-medium`}>
                      {fmtR(bet.payout_amount)}
                    </td>
                    <td className={`${tdCls} text-slate-500`}>
                      {new Date(bet.created_at).toLocaleString()}
                    </td>
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

export default Bets;
