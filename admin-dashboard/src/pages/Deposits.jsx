import React, { useState, useEffect } from 'react';
import { depositService } from '../services/depositService';
import { userService } from '../services/userService';
import toast from 'react-hot-toast';

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
  
  // Create deposit modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createFormData, setCreateFormData] = useState({
    user_id: '',
    amount: '',
    payment_method: 'bank_transfer',
    proof_type: 'reference_number',
    proof_value: '',
    notes: '',
    auto_approve: false,
  });
  const [userSearch, setUserSearch] = useState('');
  const [userSearchResults, setUserSearchResults] = useState([]);
  const [searchingUsers, setSearchingUsers] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadDeposits();
  }, [activeTab, page]);

  const loadDeposits = async () => {
    setLoading(true);
    try {
      if (activeTab === 'pending') {
        const data = await depositService.getPendingDeposits();
        setDeposits(data || []);
        setTotal(data?.length || 0);
        setTotalPages(1);
      } else {
        const data = await depositService.getDeposits(page, pageSize);
        setDeposits(data.deposits || []);
        setTotal(data.total || 0);
        setTotalPages(data.total_pages || 0);
      }
    } catch (error) {
      toast.error('Failed to load deposits');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    try {
      await depositService.approveDeposit(selectedDeposit.id);
      toast.success('Deposit approved successfully');
      setShowApproveModal(false);
      setSelectedDeposit(null);
      loadDeposits();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to approve deposit');
    }
  };

  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      toast.error('Please provide a rejection reason');
      return;
    }

    try {
      await depositService.rejectDeposit(selectedDeposit.id, rejectionReason);
      toast.success('Deposit rejected successfully');
      setShowRejectModal(false);
      setRejectionReason('');
      setSelectedDeposit(null);
      loadDeposits();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to reject deposit');
    }
  };

  // User search for create deposit
  useEffect(() => {
    const searchUsers = async () => {
      if (userSearch.trim().length < 3) {
        setUserSearchResults([]);
        return;
      }

      setSearchingUsers(true);
      try {
        const data = await userService.getUsers(1, 10, userSearch.trim(), null);
        setUserSearchResults(data.users || []);
      } catch (error) {
        console.error('Error searching users:', error);
        setUserSearchResults([]);
      } finally {
        setSearchingUsers(false);
      }
    };

    const timeoutId = setTimeout(searchUsers, 300);
    return () => clearTimeout(timeoutId);
  }, [userSearch]);

  const handleUserSelect = (user) => {
    setSelectedUser(user);
    setCreateFormData({ ...createFormData, user_id: user.id });
    setUserSearch(user.phone_number);
    setUserSearchResults([]);
  };

  const handleCreateDeposit = async (e) => {
    e.preventDefault();

    if (!selectedUser) {
      toast.error('Please select a user');
      return;
    }

    if (!createFormData.amount || parseFloat(createFormData.amount) <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    if (createFormData.proof_type && !createFormData.proof_value.trim()) {
      toast.error('Please enter a proof value (e.g., reference number)');
      return;
    }

    setCreating(true);
    try {
      const depositData = {
        user_id: parseInt(createFormData.user_id),
        amount: parseFloat(createFormData.amount),
        payment_method: createFormData.payment_method,
        proof_type: createFormData.proof_type || null,
        proof_value: createFormData.proof_value.trim() || null,
        notes: createFormData.notes.trim() || null,
        auto_approve: createFormData.auto_approve,
      };

      await depositService.createDeposit(depositData);
      toast.success(
        depositData.auto_approve
          ? 'Deposit created and approved successfully'
          : 'Deposit created successfully'
      );
      setShowCreateModal(false);
      setCreateFormData({
        user_id: '',
        amount: '',
        payment_method: 'bank_transfer',
        proof_type: 'reference_number',
        proof_value: '',
        notes: '',
        auto_approve: false,
      });
      setSelectedUser(null);
      setUserSearch('');
      loadDeposits();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create deposit');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Deposits</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          + Create Deposit
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => {
              setActiveTab('pending');
              setPage(1);
            }}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'pending'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Pending ({deposits.filter(d => d.status === 'pending').length})
          </button>
          <button
            onClick={() => {
              setActiveTab('all');
              setPage(1);
            }}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'all'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            All Deposits
          </button>
        </nav>
      </div>

      {/* Deposits Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-600">Loading deposits...</div>
        ) : deposits.length === 0 ? (
          <div className="p-8 text-center text-gray-600">No deposits found</div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {deposits.map((deposit) => (
                    <tr key={deposit.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{deposit.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{deposit.user_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">R {parseFloat(deposit.amount).toFixed(2)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{deposit.payment_method}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                          deposit.status === 'approved' ? 'bg-green-100 text-green-800' :
                          deposit.status === 'rejected' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {deposit.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(deposit.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {deposit.status === 'pending' && (
                          <>
                            <button
                              onClick={() => {
                                setSelectedDeposit(deposit);
                                setShowApproveModal(true);
                              }}
                              className="text-green-600 hover:text-green-900 mr-4"
                            >
                              Approve
                            </button>
                            <button
                              onClick={() => {
                                setSelectedDeposit(deposit);
                                setShowRejectModal(true);
                              }}
                              className="text-red-600 hover:text-red-900"
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

            {activeTab === 'all' && totalPages > 1 && (
              <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-t">
                <div className="text-sm text-gray-700">
                  Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total}
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 text-sm border rounded-md disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 text-sm border rounded-md disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Approve Modal */}
      {showApproveModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Approve Deposit</h2>
            <p className="text-gray-600 mb-4">
              Approve deposit of R{parseFloat(selectedDeposit?.amount || 0).toFixed(2)}?
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowApproveModal(false);
                  setSelectedDeposit(null);
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
              >
                Approve
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Reject Deposit</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rejection Reason (required)
              </label>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Enter reason for rejection..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectionReason('');
                  setSelectedDeposit(null);
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Deposit Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full my-8">
            <h2 className="text-xl font-bold mb-4">Create Deposit</h2>
            <form onSubmit={handleCreateDeposit}>
              {/* User Search */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  User <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={userSearch}
                    onChange={(e) => {
                      setUserSearch(e.target.value);
                      if (!e.target.value.trim()) {
                        setSelectedUser(null);
                        setCreateFormData({ ...createFormData, user_id: '' });
                      }
                    }}
                    onBlur={() => {
                      // Delay closing dropdown to allow click on results
                      setTimeout(() => setUserSearchResults([]), 200);
                    }}
                    placeholder="Search by phone number (min 3 characters)..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  {searchingUsers && (
                    <div className="absolute right-3 top-2 text-gray-400 text-sm">Searching...</div>
                  )}
                  {userSearchResults.length > 0 && !selectedUser && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                      {userSearchResults.map((user) => (
                        <button
                          key={user.id}
                          type="button"
                          onMouseDown={(e) => {
                            e.preventDefault(); // Prevent input blur
                            handleUserSelect(user);
                          }}
                          className="w-full text-left px-4 py-2 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
                        >
                          <div className="font-medium">{user.phone_number}</div>
                          <div className="text-sm text-gray-500">
                            ID: {user.id} | Balance: R{parseFloat(user.wallet_balance || 0).toFixed(2)}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {selectedUser && (
                  <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded flex justify-between items-center">
                    <span className="text-sm text-green-800">
                      Selected: {selectedUser.phone_number} (ID: {selectedUser.id})
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedUser(null);
                        setUserSearch('');
                        setCreateFormData({ ...createFormData, user_id: '' });
                      }}
                      className="text-xs text-red-600 hover:text-red-800"
                    >
                      Clear
                    </button>
                  </div>
                )}
              </div>

              {/* Amount */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Amount (R) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="10"
                  value={createFormData.amount}
                  onChange={(e) => setCreateFormData({ ...createFormData, amount: e.target.value })}
                  placeholder="0.00"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <p className="mt-1 text-xs text-gray-500">Minimum: R10.00</p>
              </div>

              {/* Payment Method */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Payment Method <span className="text-red-500">*</span>
                </label>
                <select
                  value={createFormData.payment_method}
                  onChange={(e) => setCreateFormData({ ...createFormData, payment_method: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="1voucher">1Voucher</option>
                  <option value="snapscan">SnapScan</option>
                  <option value="capitec">Capitec</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Proof Type */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Proof Type
                </label>
                <select
                  value={createFormData.proof_type}
                  onChange={(e) => setCreateFormData({ ...createFormData, proof_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="reference_number">Reference Number</option>
                  <option value="image_url">Image URL</option>
                  <option value="">None</option>
                </select>
              </div>

              {/* Proof Value */}
              {createFormData.proof_type && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {createFormData.proof_type === 'reference_number' ? 'Reference Number' : 'Image URL'}
                  </label>
                  <input
                    type="text"
                    value={createFormData.proof_value}
                    onChange={(e) => setCreateFormData({ ...createFormData, proof_value: e.target.value })}
                    placeholder={
                      createFormData.proof_type === 'reference_number'
                        ? 'Enter bank reference number...'
                        : 'Enter image URL...'
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              )}

              {/* Notes */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes
                </label>
                <textarea
                  value={createFormData.notes}
                  onChange={(e) => setCreateFormData({ ...createFormData, notes: e.target.value })}
                  placeholder="Additional notes (optional)..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              {/* Auto Approve */}
              <div className="mb-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={createFormData.auto_approve}
                    onChange={(e) => setCreateFormData({ ...createFormData, auto_approve: e.target.checked })}
                    className="mr-2 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <span className="text-sm text-gray-700">
                    Auto-approve and credit wallet immediately
                  </span>
                </label>
                <p className="mt-1 text-xs text-gray-500">
                  If checked, the deposit will be approved and the user's wallet will be credited immediately.
                </p>
              </div>

              {/* Form Actions */}
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    setCreateFormData({
                      user_id: '',
                      amount: '',
                      payment_method: 'bank_transfer',
                      proof_type: 'reference_number',
                      proof_value: '',
                      notes: '',
                      auto_approve: false,
                    });
                    setSelectedUser(null);
                    setUserSearch('');
                    setUserSearchResults([]);
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                  disabled={creating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating || !selectedUser}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {creating ? 'Creating...' : 'Create Deposit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Deposits;
