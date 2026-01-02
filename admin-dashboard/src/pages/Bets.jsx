import React, { useState, useEffect } from 'react';
import { betService } from '../services/betService';
import toast from 'react-hot-toast';

const Bets = () => {
  const [bets, setBets] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({
    bet_type: '',
    status: '',
    date_from: '',
    date_to: '',
  });

  useEffect(() => {
    loadBets();
    loadStatistics();
  }, [page, filters]);

  const loadBets = async () => {
    setLoading(true);
    try {
      const activeFilters = {};
      if (filters.bet_type) activeFilters.bet_type = filters.bet_type;
      if (filters.status) activeFilters.status = filters.status;
      if (filters.date_from) activeFilters.date_from = filters.date_from;
      if (filters.date_to) activeFilters.date_to = filters.date_to;

      const data = await betService.getBets(page, pageSize, activeFilters);
      setBets(data.bets || []);
      setTotal(data.total || 0);
    } catch (error) {
      toast.error('Failed to load bets');
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const activeFilters = {};
      if (filters.bet_type) activeFilters.bet_type = filters.bet_type;
      if (filters.date_from) activeFilters.date_from = filters.date_from;
      if (filters.date_to) activeFilters.date_to = filters.date_to;

      const data = await betService.getBetStatistics(activeFilters);
      setStatistics(data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const exportToCSV = () => {
    const headers = ['ID', 'User ID', 'Bet Type', 'Stake', 'Status', 'Payout', 'Created'];
    const rows = bets.map(bet => [
      bet.id,
      bet.user_id,
      bet.bet_type,
      bet.stake_amount,
      bet.status,
      bet.payout_amount,
      bet.created_at,
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bets-${new Date().toISOString()}.csv`;
    a.click();
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Bets</h1>
        <button
          onClick={exportToCSV}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Export CSV
        </button>
      </div>

      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Bets</div>
            <div className="text-2xl font-bold">{statistics.total_bets}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Active Bets</div>
            <div className="text-2xl font-bold text-yellow-600">{statistics.active_bets}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Total Wagered</div>
            <div className="text-2xl font-bold">R {statistics.total_wagered.toFixed(2)}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">Net Revenue</div>
            <div className={`text-2xl font-bold ${statistics.net_revenue >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              R {statistics.net_revenue.toFixed(2)}
            </div>
          </div>
        </div>
      )}

      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Bet Type</label>
            <select
              value={filters.bet_type}
              onChange={(e) => {
                setFilters({ ...filters, bet_type: e.target.value });
                setPage(1);
              }}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="">All Types</option>
              <option value="lucky_wheel">Lucky Wheel</option>
              <option value="color_game">Color Game</option>
              <option value="pick_3">Pick 3</option>
              <option value="football_yesno">Football Yes/No</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filters.status}
              onChange={(e) => {
                setFilters({ ...filters, status: e.target.value });
                setPage(1);
              }}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="won">Won</option>
              <option value="lost">Lost</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">From Date</label>
            <input
              type="date"
              value={filters.date_from}
              onChange={(e) => {
                setFilters({ ...filters, date_from: e.target.value });
                setPage(1);
              }}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">To Date</label>
            <input
              type="date"
              value={filters.date_to}
              onChange={(e) => {
                setFilters({ ...filters, date_to: e.target.value });
                setPage(1);
              }}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">Loading bets...</div>
        ) : bets.length === 0 ? (
          <div className="p-8 text-center">No bets found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stake</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Payout</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {bets.map((bet) => (
                  <tr key={bet.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{bet.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{bet.user_phone}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{bet.bet_type}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">R {bet.stake_amount.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        bet.status === 'won' ? 'bg-green-100 text-green-800' :
                        bet.status === 'lost' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {bet.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">R {bet.payout_amount.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(bet.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Bets;
