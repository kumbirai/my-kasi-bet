import React, { useState, useEffect } from 'react';
import { withdrawalService } from '../services/withdrawalService';
import toast from 'react-hot-toast';

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

  useEffect(() => {
    loadWithdrawals();
  }, [activeTab, page]);

  const loadWithdrawals = async () => {
    setLoading(true);
    try {
      if (activeTab === 'pending') {
        const data = await withdrawalService.getPendingWithdrawals();
        setWithdrawals(data || []);
        setTotal(data?.length || 0);
        setTotalPages(1);
      } else {
        const data = await withdrawalService.getWithdrawals(page, pageSize);
        setWithdrawals(data.withdrawals || []);
        setTotal(data.total || 0);
        setTotalPages(data.total_pages || 0);
      }
    } catch (error) {
      toast.error('Failed to load withdrawals');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    try {
      await withdrawalService.approveWithdrawal(selectedWithdrawal.id, paymentReference || null);
      toast.success('Withdrawal approved successfully');
      setShowApproveModal(false);
      setSelectedWithdrawal(null);
      setPaymentReference('');
      loadWithdrawals();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to approve withdrawal');
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      toast.error('Please provide a rejection reason');
      return;
    }

    try {
      await withdrawalService.rejectWithdrawal(selectedWithdrawal.id, rejectionReason);
      toast.success('Withdrawal rejected successfully');
      setShowRejectModal(false);
      setRejectionReason('');
      setSelectedWithdrawal(null);
      loadWithdrawals();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to reject withdrawal');
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-shadow-grey-900 mb-6">Withdrawals</h1>

      <div className="border-b border-shadow-grey-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => {
              setActiveTab('pending');
              setPage(1);
            }}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'pending'
                ? 'border-true-cobalt-500 text-true-cobalt-600'
                : 'border-transparent text-shadow-grey-500 hover:text-shadow-grey-700'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => {
              setActiveTab('all');
              setPage(1);
            }}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'all'
                ? 'border-true-cobalt-500 text-true-cobalt-600'
                : 'border-transparent text-shadow-grey-500 hover:text-shadow-grey-700'
            }`}
          >
            All Withdrawals
          </button>
        </nav>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-shadow-grey-600">Loading withdrawals...</div>
        ) : withdrawals.length === 0 ? (
          <div className="p-8 text-center text-shadow-grey-600">No withdrawals found</div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-shadow-grey-200">
                <thead className="bg-shadow-grey-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase">ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase">User ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase">Bank Details</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-shadow-grey-200">
                  {withdrawals.map((w) => (
                    <tr key={w.id} className="hover:bg-shadow-grey-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-shadow-grey-900">{w.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-shadow-grey-900">{w.user_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-shadow-grey-900">R {parseFloat(w.amount).toFixed(2)}</td>
                      <td className="px-6 py-4 text-sm text-shadow-grey-500">
                        {w.bank_name && <div>{w.bank_name}</div>}
                        {w.account_number && <div>Acc: {w.account_number}</div>}
                        {w.account_holder && <div>{w.account_holder}</div>}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          w.status === 'approved' ? 'bg-periwinkle-100 text-periwinkle-800' :
                          w.status === 'rejected' ? 'bg-shadow-grey-200 text-shadow-grey-800' :
                          'bg-soft-periwinkle-100 text-soft-periwinkle-800'
                        }`}>
                          {w.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-shadow-grey-500">
                        {new Date(w.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {w.status === 'pending' && (
                          <>
                            <button
                              onClick={() => {
                                setSelectedWithdrawal(w);
                                setShowApproveModal(true);
                              }}
                              className="text-periwinkle-600 hover:text-periwinkle-900 mr-4"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => {
                                setSelectedWithdrawal(w);
                                setShowRejectModal(true);
                              }}
                              className="text-shadow-grey-700 hover:text-shadow-grey-900"
                            >
                              Reject
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      {showApproveModal && (
        <div className="fixed inset-0 bg-shadow-grey-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Approve Withdrawal</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-shadow-grey-700 mb-2">
                Payment Reference (optional)
              </label>
              <input
                type="text"
                value={paymentReference}
                onChange={(e) => setPaymentReference(e.target.value)}
                placeholder="Enter payment reference..."
                className="w-full px-3 py-2 border border-shadow-grey-300 rounded-md"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowApproveModal(false);
                  setSelectedWithdrawal(null);
                  setPaymentReference('');
                }}
                className="px-4 py-2 text-sm bg-shadow-grey-100 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                className="px-4 py-2 text-sm text-white bg-periwinkle-600 rounded-md"
              >
                Approve
              </button>
            </div>
          </div>
        </div>
      )}

      {showRejectModal && (
        <div className="fixed inset-0 bg-shadow-grey-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Reject Withdrawal</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-shadow-grey-700 mb-2">
                Rejection Reason
              </label>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-shadow-grey-300 rounded-md"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectionReason('');
                  setSelectedWithdrawal(null);
                }}
                className="px-4 py-2 text-sm bg-shadow-grey-100 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                className="px-4 py-2 text-sm text-white bg-shadow-grey-700 rounded-md"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Withdrawals;
