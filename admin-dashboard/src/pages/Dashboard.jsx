import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';
import { Icon } from '../components/ui';

const StatCard = ({ title, value, icon, accent }) => (
  <div className="bg-kasi-800 border border-white/[0.05] rounded-xl p-5 hover:border-white/10 transition-colors">
    <div className={`inline-flex p-2.5 rounded-xl mb-4 ${accent}`}>
      <Icon name={icon} className="w-5 h-5" />
    </div>
    <p className="text-xl font-bold text-white leading-tight mb-0.5">{value}</p>
    <p className="text-sm text-slate-400">{title}</p>
  </div>
);

const RevenueCard = ({ title, value, positive }) => (
  <div className="bg-kasi-800 border border-white/[0.05] rounded-xl p-5">
    <p className="text-sm text-slate-400 mb-3">{title}</p>
    <p className={`text-2xl font-bold ${positive === undefined ? 'text-white' : positive ? 'text-emerald-400' : 'text-red-400'}`}>
      {value}
    </p>
  </div>
);

const SkeletonCard = () => (
  <div className="bg-kasi-800 border border-white/[0.05] rounded-xl p-5 animate-pulse">
    <div className="w-10 h-10 bg-kasi-700 rounded-xl mb-4" />
    <div className="h-6 bg-kasi-700 rounded w-20 mb-2" />
    <div className="h-4 bg-kasi-700 rounded w-28" />
  </div>
);

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_users: 0, active_users: 0, blocked_users: 0,
    total_deposits: 0, total_withdrawals: 0,
    pending_deposits: 0, pending_withdrawals: 0,
    total_bets: 0, active_bets: 0,
    total_wagered: 0, total_payouts: 0,
    net_revenue: 0, platform_balance: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
    const id = setInterval(loadStats, 30000);
    return () => clearInterval(id);
  }, []);

  const loadStats = async () => {
    try {
      const data = await analyticsService.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const fmtN = (n) => (typeof n === 'number' ? n.toLocaleString() : n ?? '—');
  const fmtR = (n) =>
    `R ${Number(n || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <span className="text-xs text-slate-600 bg-kasi-800 border border-white/[0.05] px-3 py-1.5 rounded-lg">
          Auto-refreshes every 30s
        </span>
      </div>

      {/* Primary stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <StatCard title="Total Users"          value={fmtN(stats.total_users)}          icon="users"      accent="bg-blue-500/10 text-blue-400" />
            <StatCard title="Active Bets"          value={fmtN(stats.active_bets)}          icon="bets"       accent="bg-purple-500/10 text-purple-400" />
            <StatCard title="Pending Deposits"     value={fmtN(stats.pending_deposits)}     icon="deposit"    accent="bg-amber-500/10 text-amber-400" />
            <StatCard title="Pending Withdrawals"  value={fmtN(stats.pending_withdrawals)}  icon="withdrawal" accent="bg-orange-500/10 text-orange-400" />
          </>
        )}
      </div>

      {/* Revenue row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {loading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-kasi-800 border border-white/[0.05] rounded-xl p-5 h-24 animate-pulse" />
          ))
        ) : (
          <>
            <RevenueCard title="Total Deposits"    value={fmtR(stats.total_deposits)}    positive />
            <RevenueCard title="Total Withdrawals" value={fmtR(stats.total_withdrawals)} positive={false} />
            <RevenueCard
              title="Net Revenue"
              value={fmtR(stats.net_revenue)}
              positive={stats.net_revenue >= 0}
            />
          </>
        )}
      </div>

      {/* Secondary stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <StatCard title="Total Bets"       value={fmtN(stats.total_bets)}       icon="bets"       accent="bg-purple-500/10 text-purple-400" />
            <StatCard title="Total Wagered"    value={fmtR(stats.total_wagered)}    icon="coin"       accent="bg-blue-500/10 text-blue-400" />
            <StatCard title="Total Payouts"    value={fmtR(stats.total_payouts)}    icon="wallet"     accent="bg-emerald-500/10 text-emerald-400" />
            <StatCard title="Platform Balance" value={fmtR(stats.platform_balance)} icon="wallet"     accent="bg-amber-500/10 text-amber-400" />
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
