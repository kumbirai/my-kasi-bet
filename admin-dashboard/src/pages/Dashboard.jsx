import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';

const StatCard = ({ title, value, icon, color }) => {
  const colors = {
    blue: 'text-true-cobalt-600 bg-true-cobalt-50',
    green: 'text-periwinkle-600 bg-periwinkle-50',
    yellow: 'text-soft-periwinkle-400 bg-soft-periwinkle-50',
    red: 'text-shadow-grey-700 bg-shadow-grey-100',
    purple: 'text-lavender-mist-600 bg-lavender-mist-50',
    indigo: 'text-true-cobalt-600 bg-true-cobalt-50',
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-shadow-grey-600">{title}</h3>
          <p className={`text-3xl font-bold mt-2 ${colors[color]?.split(' ')[0] || 'text-shadow-grey-900'}`}>
            {typeof value === 'number' && value >= 1000
              ? (value / 1000).toFixed(1) + 'K'
              : typeof value === 'number' && value < 1 && value > 0
              ? value.toFixed(2)
              : typeof value === 'number'
              ? value.toLocaleString()
              : value}
          </p>
        </div>
        <div className={`text-4xl ${colors[color]?.split(' ')[1] || 'bg-shadow-grey-50'} p-3 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_users: 0,
    active_users: 0,
    blocked_users: 0,
    total_deposits: 0,
    total_withdrawals: 0,
    pending_deposits: 0,
    pending_withdrawals: 0,
    total_bets: 0,
    active_bets: 0,
    total_wagered: 0,
    total_payouts: 0,
    net_revenue: 0,
    platform_balance: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardStats();
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardStats = async () => {
    try {
      const data = await analyticsService.getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-shadow-grey-600">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-shadow-grey-900 mb-6">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard
          title="Total Users"
          value={stats.total_users}
          icon="👥"
          color="blue"
        />
        <StatCard
          title="Active Bets"
          value={stats.active_bets}
          icon="🎲"
          color="green"
        />
        <StatCard
          title="Pending Deposits"
          value={stats.pending_deposits}
          icon="💰"
          color="yellow"
        />
        <StatCard
          title="Pending Withdrawals"
          value={stats.pending_withdrawals}
          icon="💸"
          color="red"
        />
      </div>

      {/* Revenue Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-shadow-grey-600">Total Deposits</h3>
          <p className="text-3xl font-bold text-periwinkle-600 mt-2">
            R {stats.total_deposits.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-shadow-grey-600">Total Withdrawals</h3>
          <p className="text-3xl font-bold text-shadow-grey-700 mt-2">
            R {stats.total_withdrawals.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-shadow-grey-600">Net Revenue</h3>
          <p className={`text-3xl font-bold mt-2 ${stats.net_revenue >= 0 ? 'text-periwinkle-600' : 'text-shadow-grey-700'}`}>
            R {stats.net_revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Bets"
          value={stats.total_bets}
          icon="🎯"
          color="purple"
        />
        <StatCard
          title="Total Wagered"
          value={`R ${stats.total_wagered.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon="💵"
          color="indigo"
        />
        <StatCard
          title="Total Payouts"
          value={`R ${stats.total_payouts.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon="🏆"
          color="green"
        />
        <StatCard
          title="Platform Balance"
          value={`R ${stats.platform_balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon="💳"
          color="blue"
        />
      </div>
    </div>
  );
};

export default Dashboard;
