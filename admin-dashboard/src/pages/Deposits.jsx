import React, { useState, useEffect } from 'react';
import { depositService } from '../services/depositService';
import { userService } from '../services/userService';
import toast from 'react-hot-toast';
import {
  Icon, Badge, Modal, Pagination, SkeletonRows,
  tableCls, theadCls, thCls, tdCls, trHoverCls,
  inputCls, selectCls, labelCls, textareaCls,
  btnPrimary, btnSecondary, btnDanger, btnSuccess,
} from '../components/ui';

const EMPTY_CREATE = {
  user_id: '', amount: '', payment_method: 'bank_transfer',
  proof_type: 'reference_number', proof_value: '', notes: '', auto_approve: false,
};

const Deposits = () => {
  const [activeTab, setActiveTab] = useState('pending');
  const [deposits, setDeposits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [selectedDeposit, setSelectedDeposit] = useState(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createFormData, setCreateFormData] = useState(EMPTY_CREATE);
  const [userSearch, setUserSearch] = useState('');
  const [userSearchResults, setUserSearchResults] = useState([]);
  const [searchingUsers, setSearchingUsers] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [creating, setCreating] = useState(false);

  useEffect(() => { loadDeposits(); }, [activeTab, page]);

  const loadDeposits = async () => {
    setLoading(true);
    try {
      if (activeTab === 'pending') {
        const data = await depositService.getPendingDeposits();
        setDeposits(data || []); setTotal(data?.length || 0); setTotalPages(1);
      } else {
        const data = await depositService.getDeposits(page, pageSize);
        setDeposits(data.deposits || []); setTotal(data.total || 0); setTotalPages(data.total_pages || 0);
      }
    } catch { toast.error('Failed to load deposits'); }
    finally { setLoading(false); }
  };

  const handleApprove = async () => {
    try {
      await depositService.approveDeposit(selectedDeposit.id);
      toast.success('Deposit approved');
      setShowApproveModal(false); setSelectedDeposit(null); loadDeposits();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to approve deposit'); }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) { toast.error('Please provide a rejection reason'); return; }
    try {
      await depositService.rejectDeposit(selectedDeposit.id, rejectionReason);
      toast.success('Deposit rejected');
      setShowRejectModal(false); setRejectionReason(''); setSelectedDeposit(null); loadDeposits();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to reject deposit'); }
  };

  useEffect(() => {
    const search = async () => {
      if (userSearch.trim().length < 3) { setUserSearchResults([]); return; }
      setSearchingUsers(true);
      try {
        const data = await userService.getUsers(1, 10, userSearch.trim(), null);
        setUserSearchResults(data.users || []);
      } catch { setUserSearchResults([]); }
      finally { setSearchingUsers(false); }
    };
    const t = setTimeout(search, 300);
    return () => clearTimeout(t);
  }, [userSearch]);

  const handleUserSelect = (user) => {
    setSelectedUser(user);
    setCreateFormData((f) => ({ ...f, user_id: user.id }));
    setUserSearch(user.phone_number);
    setUserSearchResults([]);
  };

  const handleCreateDeposit = async (e) => {
    e.preventDefault();
    if (!selectedUser) { toast.error('Please select a user'); return; }
    if (!createFormData.amount || parseFloat(createFormData.amount) <= 0) { toast.error('Enter a valid amount'); return; }
    if (createFormData.proof_type && !createFormData.proof_value.trim()) { toast.error('Enter a proof value'); return; }
    setCreating(true);
    try {
      await depositService.createDeposit({
        user_id: parseInt(createFormData.user_id),
        amount: parseFloat(createFormData.amount),
        payment_method: createFormData.payment_method,
        proof_type: createFormData.proof_type || null,
        proof_value: createFormData.proof_value.trim() || null,
        notes: createFormData.notes.trim() || null,
        auto_approve: createFormData.auto_approve,
      });
      toast.success(createFormData.auto_approve ? 'Deposit created and approved' : 'Deposit created');
      closeCreateModal(); loadDeposits();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to create deposit'); }
    finally { setCreating(false); }
  };

  const closeCreateModal = () => {
    setShowCreateModal(false); setCreateFormData(EMPTY_CREATE);
    setSelectedUser(null); setUserSearch(''); setUserSearchResults([]);
  };
  const setField = (k, v) => setCreateFormData((f) => ({ ...f, [k]: v }));
  const fmtR = (n) => `R ${parseFloat(n || 0).toFixed(2)}`;
  const pendingCount = deposits.filter((d) => d.status === 'pending').length;

  const TabBtn = ({ id, label }) => (
    <button
      onClick={() => { setActiveTab(id); setPage(1); }}
      className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
        activeTab === id
          ? 'bg-blue-500/15 text-blue-400 border border-blue-500/20'
          : 'text-slate-400 hover:text-white hover:bg-white/[0.05]'
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Deposits</h1>
        <button onClick={() => setShowCreateModal(true)} className={btnPrimary}>
          <Icon name="plus" className="w-4 h-4" />
          Create Deposit
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        <TabBtn id="pending" label={`Pending${activeTab === 'pending' && pendingCount > 0 ? ` (${pendingCount})` : ''}`} />
        <TabBtn id="all" label="All Deposits" />
      </div>

      {/* Table */}
      <div className={tableCls}>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className={theadCls}>
              <tr>
                <th className={thCls}>ID</th>
                <th className={thCls}>User ID</th>
                <th className={thCls}>Amount</th>
                <th className={thCls}>Method</th>
                <th className={thCls}>Status</th>
                <th className={thCls}>Created</th>
                <th className={thCls}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <SkeletonRows cols={7} rows={8} />
              ) : deposits.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-14 text-center text-slate-500 text-sm">No deposits found</td>
                </tr>
              ) : (
                deposits.map((dep) => (
                  <tr key={dep.id} className={trHoverCls}>
                    <td className={`${tdCls} font-mono text-xs text-slate-500`}>{dep.id}</td>
                    <td className={tdCls}>{dep.user_id}</td>
                    <td className={`${tdCls} text-amber-400 font-medium`}>{fmtR(dep.amount)}</td>
                    <td className={`${tdCls} text-slate-400`}>{dep.payment_method}</td>
                    <td className={tdCls}><Badge status={dep.status} /></td>
                    <td className={`${tdCls} text-slate-500`}>{new Date(dep.created_at).toLocaleString()}</td>
                    <td className={tdCls}>
                      {dep.status === 'pending' && (
                        <div className="flex gap-3">
                          <button
                            onClick={() => { setSelectedDeposit(dep); setShowApproveModal(true); }}
                            className="text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors cursor-pointer"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => { setSelectedDeposit(dep); setShowRejectModal(true); }}
                            className="text-xs font-medium text-red-400 hover:text-red-300 transition-colors cursor-pointer"
                          >
                            Reject
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {activeTab === 'all' && (
          <Pagination page={page} totalPages={totalPages} total={total} pageSize={pageSize} onPage={setPage} />
        )}
      </div>

      {/* Approve modal */}
      <Modal open={showApproveModal} onClose={() => { setShowApproveModal(false); setSelectedDeposit(null); }} title="Approve Deposit">
        <p className="text-sm text-slate-400 mb-5">
          Approve deposit of <span className="text-amber-400 font-semibold">{fmtR(selectedDeposit?.amount)}</span> for user {selectedDeposit?.user_id}?
        </p>
        <div className="flex justify-end gap-3">
          <button onClick={() => { setShowApproveModal(false); setSelectedDeposit(null); }} className={btnSecondary}>Cancel</button>
          <button onClick={handleApprove} className={btnSuccess}>
            <Icon name="check" className="w-4 h-4" />
            Approve
          </button>
        </div>
      </Modal>

      {/* Reject modal */}
      <Modal open={showRejectModal} onClose={() => { setShowRejectModal(false); setRejectionReason(''); setSelectedDeposit(null); }} title="Reject Deposit">
        <div className="mb-5">
          <label className={labelCls}>Rejection Reason <span className="text-red-400">*</span></label>
          <textarea value={rejectionReason} onChange={(e) => setRejectionReason(e.target.value)} placeholder="Enter reason…" rows={3} className={textareaCls} />
        </div>
        <div className="flex justify-end gap-3">
          <button onClick={() => { setShowRejectModal(false); setRejectionReason(''); setSelectedDeposit(null); }} className={btnSecondary}>Cancel</button>
          <button onClick={handleReject} className={btnDanger}>Reject</button>
        </div>
      </Modal>

      {/* Create modal */}
      <Modal open={showCreateModal} onClose={closeCreateModal} title="Create Deposit" maxWidth="max-w-2xl">
        <form onSubmit={handleCreateDeposit} className="space-y-4">
          {/* User search */}
          <div>
            <label className={labelCls}>User <span className="text-red-400">*</span></label>
            <div className="relative">
              <input
                type="text"
                value={userSearch}
                onChange={(e) => { setUserSearch(e.target.value); if (!e.target.value.trim()) { setSelectedUser(null); setField('user_id', ''); } }}
                onBlur={() => setTimeout(() => setUserSearchResults([]), 200)}
                placeholder="Search by phone number (min 3 chars)…"
                className={inputCls}
              />
              {searchingUsers && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  <svg className="animate-spin w-4 h-4 text-slate-500" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                </div>
              )}
              {userSearchResults.length > 0 && !selectedUser && (
                <div className="absolute z-10 w-full mt-1 bg-kasi-750 border border-white/10 rounded-xl shadow-2xl max-h-52 overflow-auto">
                  {userSearchResults.map((user) => (
                    <button
                      key={user.id}
                      type="button"
                      onMouseDown={(e) => { e.preventDefault(); handleUserSelect(user); }}
                      className="w-full text-left px-4 py-3 hover:bg-kasi-700 transition-colors cursor-pointer border-b border-white/[0.04] last:border-0"
                    >
                      <p className="text-sm font-medium text-white">{user.phone_number}</p>
                      <p className="text-xs text-slate-500">ID: {user.id} &middot; Balance: R{parseFloat(user.wallet_balance || 0).toFixed(2)}</p>
                    </button>
                  ))}
                </div>
              )}
            </div>
            {selectedUser && (
              <div className="mt-2 flex items-center justify-between px-3 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                <span className="text-sm text-blue-300">{selectedUser.phone_number} (ID: {selectedUser.id})</span>
                <button type="button" onClick={() => { setSelectedUser(null); setUserSearch(''); setField('user_id', ''); }} className="text-xs text-slate-500 hover:text-white cursor-pointer transition-colors">
                  Clear
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelCls}>Amount (R) <span className="text-red-400">*</span></label>
              <input type="number" step="0.01" min="10" value={createFormData.amount} onChange={(e) => setField('amount', e.target.value)} placeholder="0.00" required className={inputCls} />
              <p className="mt-1 text-xs text-slate-600">Minimum R10.00</p>
            </div>
            <div>
              <label className={labelCls}>Payment Method <span className="text-red-400">*</span></label>
              <select value={createFormData.payment_method} onChange={(e) => setField('payment_method', e.target.value)} required className={selectCls}>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="1voucher">1Voucher</option>
                <option value="snapscan">SnapScan</option>
                <option value="capitec">Capitec</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelCls}>Proof Type</label>
              <select value={createFormData.proof_type} onChange={(e) => setField('proof_type', e.target.value)} className={selectCls}>
                <option value="reference_number">Reference Number</option>
                <option value="image_url">Image URL</option>
                <option value="">None</option>
              </select>
            </div>
            {createFormData.proof_type && (
              <div>
                <label className={labelCls}>{createFormData.proof_type === 'reference_number' ? 'Reference Number' : 'Image URL'}</label>
                <input type="text" value={createFormData.proof_value} onChange={(e) => setField('proof_value', e.target.value)} placeholder={createFormData.proof_type === 'reference_number' ? 'Bank reference…' : 'Image URL…'} className={inputCls} />
              </div>
            )}
          </div>

          <div>
            <label className={labelCls}>Notes</label>
            <textarea value={createFormData.notes} onChange={(e) => setField('notes', e.target.value)} placeholder="Additional notes (optional)…" rows={2} className={textareaCls} />
          </div>

          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={createFormData.auto_approve}
              onChange={(e) => setField('auto_approve', e.target.checked)}
              className="mt-0.5 w-4 h-4 rounded bg-kasi-750 border border-white/10 accent-blue-500"
            />
            <span className="text-sm text-slate-300">
              Auto-approve and credit wallet immediately
            </span>
          </label>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={closeCreateModal} disabled={creating} className={btnSecondary}>Cancel</button>
            <button type="submit" disabled={creating || !selectedUser} className={btnPrimary}>
              {creating ? (
                <>
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Creating…
                </>
              ) : 'Create Deposit'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Deposits;
