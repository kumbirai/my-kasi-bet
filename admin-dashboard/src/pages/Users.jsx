import React, { useState, useEffect } from 'react';
import { userService } from '../services/userService';
import toast from 'react-hot-toast';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [search, setSearch] = useState('');
  const [filterBlocked, setFilterBlocked] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [blockReason, setBlockReason] = useState('');

  useEffect(() => {
    loadUsers();
  }, [page, search, filterBlocked]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await userService.getUsers(page, pageSize, search || null, filterBlocked);
      setUsers(data.users || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 0);
    } catch (error) {
      toast.error('Failed to load users');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleBlock = async () => {
    if (!selectedUser || !blockReason.trim()) {
      toast.error('Please provide a reason');
      return;
    }

    try {
      await userService.blockUser(selectedUser.id, blockReason);
      toast.success('User blocked successfully');
      setShowBlockModal(false);
      setBlockReason('');
      setSelectedUser(null);
      loadUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to block user');
    }
  };

  const handleUnblock = async (user) => {
    if (!window.confirm(`Are you sure you want to unblock ${user.phone_number}?`)) {
      return;
    }

    try {
      await userService.unblockUser(user.id);
      toast.success('User unblocked successfully');
      loadUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to unblock user');
    }
  };

  const handleSearch = (e) => {
    setSearch(e.target.value);
    setPage(1);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-shadow-grey-900">Users</h1>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-shadow-grey-700 mb-2">
              Search by Phone
            </label>
            <input
              type="text"
              value={search}
              onChange={handleSearch}
              placeholder="Enter phone number..."
              className="w-full px-3 py-2 border border-shadow-grey-300 rounded-md focus:outline-none focus:ring-2 focus:ring-true-cobalt-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-shadow-grey-700 mb-2">
              Filter by Status
            </label>
            <select
              value={filterBlocked === null ? 'all' : filterBlocked ? 'blocked' : 'active'}
              onChange={(e) => {
                const value = e.target.value;
                setFilterBlocked(value === 'all' ? null : value === 'blocked');
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-shadow-grey-300 rounded-md focus:outline-none focus:ring-2 focus:ring-true-cobalt-500"
            >
              <option value="all">All Users</option>
              <option value="active">Active Only</option>
              <option value="blocked">Blocked Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-shadow-grey-600">Loading users...</div>
        ) : users.length === 0 ? (
          <div className="p-8 text-center text-shadow-grey-600">No users found</div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-shadow-grey-200">
                <thead className="bg-shadow-grey-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase tracking-wider">
                      Phone Number
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase tracking-wider">
                      Balance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-shadow-grey-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-shadow-grey-200">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-shadow-grey-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-shadow-grey-900">
                        {user.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-shadow-grey-900">
                        {user.phone_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-shadow-grey-900">
                        R {user.wallet_balance.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            user.is_blocked
                              ? 'bg-shadow-grey-200 text-shadow-grey-800'
                              : 'bg-periwinkle-100 text-periwinkle-800'
                          }`}
                        >
                          {user.is_blocked ? 'Blocked' : 'Active'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-shadow-grey-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {user.is_blocked ? (
                          <button
                            onClick={() => handleUnblock(user)}
                            className="text-true-cobalt-600 hover:text-true-cobalt-900 mr-4"
                          >
                            Unblock
                          </button>
                        ) : (
                          <button
                            onClick={() => {
                              setSelectedUser(user);
                              setShowBlockModal(true);
                            }}
                            className="text-shadow-grey-700 hover:text-shadow-grey-900"
                          >
                            Block
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="bg-shadow-grey-50 px-4 py-3 flex items-center justify-between border-t border-shadow-grey-200">
                <div className="text-sm text-shadow-grey-700">
                  Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, total)} of {total} users
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 text-sm font-medium text-shadow-grey-700 bg-white border border-shadow-grey-300 rounded-md hover:bg-shadow-grey-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 text-sm font-medium text-shadow-grey-700 bg-white border border-shadow-grey-300 rounded-md hover:bg-shadow-grey-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Block Modal */}
      {showBlockModal && (
        <div className="fixed inset-0 bg-shadow-grey-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Block User</h2>
            <p className="text-shadow-grey-600 mb-4">
              Are you sure you want to block {selectedUser?.phone_number}?
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-shadow-grey-700 mb-2">
                Reason (required)
              </label>
              <textarea
                value={blockReason}
                onChange={(e) => setBlockReason(e.target.value)}
                placeholder="Enter reason for blocking..."
                rows={4}
                className="w-full px-3 py-2 border border-shadow-grey-300 rounded-md focus:outline-none focus:ring-2 focus:ring-true-cobalt-500"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowBlockModal(false);
                  setBlockReason('');
                  setSelectedUser(null);
                }}
                className="px-4 py-2 text-sm font-medium text-shadow-grey-700 bg-shadow-grey-100 rounded-md hover:bg-shadow-grey-200"
              >
                Cancel
              </button>
              <button
                onClick={handleBlock}
                className="px-4 py-2 text-sm font-medium text-white bg-shadow-grey-700 rounded-md hover:bg-shadow-grey-800"
              >
                Block User
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users;
