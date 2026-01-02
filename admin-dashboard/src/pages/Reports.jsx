import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';

const Reports = () => {
  const [revenueBreakdown, setRevenueBreakdown] = useState([]);
  const [userEngagement, setUserEngagement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    loadData();
  }, [dateFrom, dateTo]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [revenue, engagement] = await Promise.all([
        analyticsService.getRevenueBreakdown(dateFrom || null, dateTo || null),
        analyticsService.getUserEngagement(),
      ]);
      setRevenueBreakdown(revenue || []);
      setUserEngagement(engagement);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Loading reports...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Analytics & Reports</h1>

      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">From Date</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">To Date</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
        </div>
      </div>

      {userEngagement && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-bold mb-4">User Engagement</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-600">Total Users</div>
              <div className="text-2xl font-bold">{userEngagement.total_users}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Active (24h)</div>
              <div className="text-2xl font-bold">{userEngagement.active_users_24h}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Active (7d)</div>
              <div className="text-2xl font-bold">{userEngagement.active_users_7d}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Active (30d)</div>
              <div className="text-2xl font-bold">{userEngagement.active_users_30d}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">New Today</div>
              <div className="text-2xl font-bold">{userEngagement.new_users_today}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">New (7d)</div>
              <div className="text-2xl font-bold">{userEngagement.new_users_7d}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Avg Bets/User</div>
              <div className="text-2xl font-bold">{userEngagement.average_bets_per_user.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Avg Deposit/User</div>
              <div className="text-2xl font-bold">R {userEngagement.average_deposit_per_user.toFixed(2)}</div>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">Revenue Breakdown by Game Type</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Game Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Wagered</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Payouts</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Net Revenue</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bet Count</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {revenueBreakdown.map((item) => (
                  <tr key={item.game_type} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{item.game_type}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">R {item.total_wagered.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">R {item.total_payouts.toFixed(2)}</td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${
                      item.net_revenue >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      R {item.net_revenue.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{item.bet_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;
