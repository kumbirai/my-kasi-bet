import React, { useState, useEffect } from 'react';
import { withdrawalService } from '../services/withdrawalService';
import toast from 'react-hot-toast';
import {
  Icon, Badge, Modal, Pagination, SkeletonRows,
  tableCls, theadCls, thCls, tdCls, trHoverCls,
  inputCls, labelCls, textareaCls,
  btnSecondary, btnDanger, btnSuccess,
} from '../components/ui';

const Withdrawals = () => {
  const [activeTab, setActiveTab] = useState('pending');
  const [withdrawals, setWithdrawals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [selectedWithdrawal, setSelectedWithdrawal] = useState(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [paymentReference, setPaymentReference] = useState('');

  useEffect(() => { loadWithdrawals(); }, [activeTab, page]);

  const loadWithdrawals = async () => {
    setLoading(true);
    try {
      if (activeTab === 'pending') {
        const data = await withdrawalService.getPendingWithdrawals();
        setWithdrawals(data || []); setTotal(data?.length || 0); setTotalPages(1);
      } else {
        const data = await withdrawalService.getWithdrawals(page, pageSize);
        setWithdrawals(data.withdrawals || []); setTotal(data.total || 0); setTotalPages(data.total_pages || 0);
      }
    } catch { toast.error('Failed to load withdrawals'); }
    finally { setLoading(false); }
  };

  const handleApprove = async () => {
    try {
      await withdrawalService.approveWithdrawal(selectedWithdrawal.id, paymentReference || null);
      toast.success('Withdrawal approved');
      setShowApproveModal(false); setSelectedWithdrawal(null); setPaymentReference(''); loadWithdrawals();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to approve withdrawal'); }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) { toast.error('Please provide a rejection reason'); return; }
    try {
      await withdrawalService.rejectWithdrawal(selectedWithdrawal.id, rejectionReason);
      toast.success('Withdrawal rejected');
      setShowRejectModal(false); setRejectionReason(''); setSelectedWithdrawal(null); loadWithdrawals();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to reject withdrawal'); }
  };

  const fmtR = (n) => `R ${parseFloat(n || 0).toFixed(2)}`;

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
      <h1 className="text-2xl font-bold text-white">Withdrawals</h1>

      {/* Tabs */}
      <div className="flex gap-2">
        <TabBtn id="pending" label="Pending" />
        <TabBtn id="all" label="All Withdrawals" />
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
                <th className={thCls}>Bank Details</th>
                <th className={thCls}>Status</th>
                <th className={thCls}>Created</th>
                <th className={thCls}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <SkeletonRows cols={7} rows={8} />
              ) : withdrawals.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-14 text-center text-slate-500 text-sm">No withdrawals found</td>
                </tr>
              ) : (
                withdrawals.map((w) => (
                  <tr key={w.id} className={trHoverCls}>
                    <td className={`${tdCls} font-mono text-xs text-slate-500`}>{w.id}</td>
                    <td className={tdCls}>{w.user_id}</td>
                    <td className={`${tdCls} text-amber-400 font-medium`}>{fmtR(w.amount)}</td>
                    <td className={tdCls}>
                      <div className="text-sm text-slate-300 leading-relaxed">
                        {w.bank_name && <p className="font-medium">{w.bank_name}</p>}
                        {w.account_number && <p className="text-slate-500 font-mono text-xs">Acc: {w.account_number}</p>}
                        {w.account_holder && <p className="text-slate-500 text-xs">{w.account_holder}</p>}
                      </div>
                    </td>
                    <td className={tdCls}><Badge status={w.status} /></td>
                    <td className={`${tdCls} text-slate-500`}>{new Date(w.created_at).toLocaleString()}</td>
                    <td className={tdCls}>
                      {w.status === 'pending' && (
                        <div className="flex gap-3">
                          <button
                            onClick={() => { setSelectedWithdrawal(w); setShowApproveModal(true); }}
                            className="text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors cursor-pointer"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => { setSelectedWithdrawal(w); setShowRejectModal(true); }}
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
      <Modal
        open={showApproveModal}
        onClose={() => { setShowApproveModal(false); setSelectedWithdrawal(null); setPaymentReference(''); }}
        title="Approve Withdrawal"
      >
        <p className="text-sm text-slate-400 mb-4">
          Approve withdrawal of <span className="text-amber-400 font-semibold">{fmtR(selectedWithdrawal?.amount)}</span> for user {selectedWithdrawal?.user_id}?
        </p>
        <div className="mb-5">
          <label className={labelCls}>Payment Reference <span className="text-slate-500">(optional)</span></label>
          <input
            type="text"
            value={paymentReference}
            onChange={(e) => setPaymentReference(e.target.value)}
            placeholder="Enter payment reference…"
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3">
          <button onClick={() => { setShowApproveModal(false); setSelectedWithdrawal(null); setPaymentReference(''); }} className={btnSecondary}>Cancel</button>
          <button onClick={handleApprove} className={btnSuccess}>
            <Icon name="check" className="w-4 h-4" />
            Approve
          </button>
        </div>
      </Modal>

      {/* Reject modal */}
      <Modal
        open={showRejectModal}
        onClose={() => { setShowRejectModal(false); setRejectionReason(''); setSelectedWithdrawal(null); }}
        title="Reject Withdrawal"
      >
        <div className="mb-5">
          <label className={labelCls}>Rejection Reason <span className="text-red-400">*</span></label>
          <textarea
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection…"
            rows={3}
            className={textareaCls}
          />
        </div>
        <div className="flex justify-end gap-3">
          <button onClick={() => { setShowRejectModal(false); setRejectionReason(''); setSelectedWithdrawal(null); }} className={btnSecondary}>Cancel</button>
          <button onClick={handleReject} className={btnDanger}>Reject</button>
        </div>
      </Modal>
    </div>
  );
};

export default Withdrawals;
