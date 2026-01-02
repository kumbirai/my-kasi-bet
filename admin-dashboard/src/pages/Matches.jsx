import React, { useState, useEffect } from 'react';
import { matchService } from '../services/matchService';
import toast from 'react-hot-toast';

const Matches = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSettleModal, setShowSettleModal] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [formData, setFormData] = useState({
    home_team: '',
    away_team: '',
    event_description: '',
    yes_odds: '',
    no_odds: '',
  });
  const [settleResult, setSettleResult] = useState('yes');

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const data = await matchService.getMatches();
      setMatches(data || []);
    } catch (error) {
      toast.error('Failed to load matches');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await matchService.createMatch({
        ...formData,
        yes_odds: parseFloat(formData.yes_odds),
        no_odds: parseFloat(formData.no_odds),
      });
      toast.success('Match created successfully');
      setShowCreateModal(false);
      setFormData({
        home_team: '',
        away_team: '',
        event_description: '',
        yes_odds: '',
        no_odds: '',
      });
      loadMatches();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create match');
    }
  };

  const handleSettle = async () => {
    try {
      await matchService.settleMatch(selectedMatch.id, settleResult);
      toast.success('Match settled successfully');
      setShowSettleModal(false);
      setSelectedMatch(null);
      loadMatches();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to settle match');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Matches</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Create Match
        </button>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">Loading matches...</div>
        ) : matches.length === 0 ? (
          <div className="p-8 text-center">No matches found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Match</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Event</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Yes Odds</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">No Odds</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {matches.map((match) => (
                  <tr key={match.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{match.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {match.home_team} vs {match.away_team}
                    </td>
                    <td className="px-6 py-4 text-sm">{match.event_description}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{match.yes_odds}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{match.no_odds}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        match.status === 'settled' ? 'bg-green-100 text-green-800' :
                        match.status === 'active' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {match.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {match.status === 'active' && (
                        <button
                          onClick={() => {
                            setSelectedMatch(match);
                            setShowSettleModal(true);
                          }}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Settle
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Create Match</h2>
            <form onSubmit={handleCreate}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Home Team</label>
                  <input
                    type="text"
                    required
                    value={formData.home_team}
                    onChange={(e) => setFormData({ ...formData, home_team: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Away Team</label>
                  <input
                    type="text"
                    required
                    value={formData.away_team}
                    onChange={(e) => setFormData({ ...formData, away_team: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Event Description</label>
                  <input
                    type="text"
                    required
                    value={formData.event_description}
                    onChange={(e) => setFormData({ ...formData, event_description: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Yes Odds</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={formData.yes_odds}
                      onChange={(e) => setFormData({ ...formData, yes_odds: e.target.value })}
                      className="w-full px-3 py-2 border rounded-md"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">No Odds</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={formData.no_odds}
                      onChange={(e) => setFormData({ ...formData, no_odds: e.target.value })}
                      className="w-full px-3 py-2 border rounded-md"
                    />
                  </div>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm bg-gray-100 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm text-white bg-indigo-600 rounded-md"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showSettleModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Settle Match</h2>
            <p className="mb-4">{selectedMatch?.home_team} vs {selectedMatch?.away_team}</p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Result</label>
              <select
                value={settleResult}
                onChange={(e) => setSettleResult(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowSettleModal(false);
                  setSelectedMatch(null);
                }}
                className="px-4 py-2 text-sm bg-gray-100 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleSettle}
                className="px-4 py-2 text-sm text-white bg-indigo-600 rounded-md"
              >
                Settle
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Matches;
