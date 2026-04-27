import React, { useState, useEffect } from 'react';
import { matchService } from '../services/matchService';
import toast from 'react-hot-toast';
import {
  Icon, Badge, Modal, SkeletonRows,
  tableCls, theadCls, thCls, tdCls, trHoverCls,
  inputCls, selectCls, labelCls, btnPrimary, btnSecondary, btnSuccess,
} from '../components/ui';

const EMPTY_FORM = { home_team: '', away_team: '', event_description: '', yes_odds: '', no_odds: '' };

const Matches = () => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSettleModal, setShowSettleModal] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [settleResult, setSettleResult] = useState('yes');

  useEffect(() => { loadMatches(); }, []);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const data = await matchService.getMatches();
      setMatches(data || []);
    } catch {
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
      toast.success('Match created');
      setShowCreateModal(false);
      setFormData(EMPTY_FORM);
      loadMatches();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create match');
    }
  };

  const handleSettle = async () => {
    try {
      await matchService.settleMatch(selectedMatch.id, settleResult);
      toast.success('Match settled');
      setShowSettleModal(false);
      setSelectedMatch(null);
      loadMatches();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to settle match');
    }
  };

  const field = (key, val) => setFormData((f) => ({ ...f, [key]: val }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Matches</h1>
        <button onClick={() => setShowCreateModal(true)} className={btnPrimary}>
          <Icon name="plus" className="w-4 h-4" />
          Create Match
        </button>
      </div>

      {/* Table */}
      <div className={tableCls}>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className={theadCls}>
              <tr>
                <th className={thCls}>ID</th>
                <th className={thCls}>Match</th>
                <th className={thCls}>Event</th>
                <th className={thCls}>Yes Odds</th>
                <th className={thCls}>No Odds</th>
                <th className={thCls}>Status</th>
                <th className={thCls}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <SkeletonRows cols={7} rows={6} />
              ) : matches.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-14 text-center text-slate-500 text-sm">
                    No matches found
                  </td>
                </tr>
              ) : (
                matches.map((match) => (
                  <tr key={match.id} className={trHoverCls}>
                    <td className={`${tdCls} font-mono text-xs text-slate-500`}>{match.id}</td>
                    <td className={`${tdCls} font-medium text-white`}>
                      {match.home_team} <span className="text-slate-500 font-normal">vs</span> {match.away_team}
                    </td>
                    <td className={`${tdCls} text-slate-400 max-w-xs truncate`}>{match.event_description}</td>
                    <td className={`${tdCls} text-emerald-400 font-mono font-medium`}>{match.yes_odds}</td>
                    <td className={`${tdCls} text-red-400 font-mono font-medium`}>{match.no_odds}</td>
                    <td className={tdCls}><Badge status={match.status} /></td>
                    <td className={tdCls}>
                      {match.status === 'active' && (
                        <button
                          onClick={() => { setSelectedMatch(match); setShowSettleModal(true); }}
                          className="text-xs font-medium text-amber-400 hover:text-amber-300 transition-colors cursor-pointer"
                        >
                          Settle
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create modal */}
      <Modal
        open={showCreateModal}
        onClose={() => { setShowCreateModal(false); setFormData(EMPTY_FORM); }}
        title="Create Match"
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelCls}>Home Team</label>
              <input type="text" required value={formData.home_team} onChange={(e) => field('home_team', e.target.value)} className={inputCls} placeholder="e.g. Kaizer Chiefs" />
            </div>
            <div>
              <label className={labelCls}>Away Team</label>
              <input type="text" required value={formData.away_team} onChange={(e) => field('away_team', e.target.value)} className={inputCls} placeholder="e.g. Orlando Pirates" />
            </div>
          </div>
          <div>
            <label className={labelCls}>Event Description</label>
            <input type="text" required value={formData.event_description} onChange={(e) => field('event_description', e.target.value)} className={inputCls} placeholder="Will Kaizer Chiefs win?" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelCls}>Yes Odds</label>
              <input type="number" step="0.01" min="1" required value={formData.yes_odds} onChange={(e) => field('yes_odds', e.target.value)} className={inputCls} placeholder="1.90" />
            </div>
            <div>
              <label className={labelCls}>No Odds</label>
              <input type="number" step="0.01" min="1" required value={formData.no_odds} onChange={(e) => field('no_odds', e.target.value)} className={inputCls} placeholder="2.10" />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => { setShowCreateModal(false); setFormData(EMPTY_FORM); }} className={btnSecondary}>
              Cancel
            </button>
            <button type="submit" className={btnPrimary}>Create Match</button>
          </div>
        </form>
      </Modal>

      {/* Settle modal */}
      <Modal
        open={showSettleModal}
        onClose={() => { setShowSettleModal(false); setSelectedMatch(null); }}
        title="Settle Match"
      >
        {selectedMatch && (
          <>
            <p className="text-sm text-slate-400 mb-1">Settling result for:</p>
            <p className="text-base font-semibold text-white mb-4">
              {selectedMatch.home_team} <span className="text-slate-500 font-normal">vs</span> {selectedMatch.away_team}
            </p>
            <div className="mb-5">
              <label className={labelCls}>Outcome</label>
              <select value={settleResult} onChange={(e) => setSettleResult(e.target.value)} className={selectCls}>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
            <div className="flex justify-end gap-3">
              <button onClick={() => { setShowSettleModal(false); setSelectedMatch(null); }} className={btnSecondary}>
                Cancel
              </button>
              <button onClick={handleSettle} className={btnSuccess}>
                <Icon name="check" className="w-4 h-4" />
                Confirm Settlement
              </button>
            </div>
          </>
        )}
      </Modal>
    </div>
  );
};

export default Matches;
