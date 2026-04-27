import React, { useState, useEffect } from 'react';
import { userService } from '../services/userService';
import toast from 'react-hot-toast';
import {
  Icon, Badge, Modal, Pagination, SkeletonRows,
  tableCls, theadCls, thCls, tdCls, trHoverCls,
  inputCls, selectCls, labelCls, textareaCls,
  btnPrimary, btnSecondary, btnDanger,
} from '../components/ui';

function userSummary(user) {
  if (!user) return '';
  if (user.phone_number && user.telegram_chat_id)
    return `User #${user.id} (${user.phone_number}, Telegram: ${user.telegram_chat_id})`;
  if (user.phone_number) return `User #${user.id} (${user.phone_number})`;
  if (user.telegram_chat_id) return `User #${user.id} (Telegram: ${user.telegram_chat_id})`;
  return `User #${user.id}`;
}

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

  useEffect(() => { loadUsers(); }, [page, search, filterBlocked]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await userService.getUsers(page, pageSize, search || null, filterBlocked);
      setUsers(data.users || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 0);
    } catch {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleBlock = async () => {
    if (!selectedUser || !blockReason.trim()) { toast.error('Please provide a reason'); return; }
    try {
      await userService.blockUser(selectedUser.id, blockReason);
      toast.success('User blocked');
      closeBlockModal();
      loadUsers();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to block user');
    }
  };

  const handleUnblock = async (user) => {
    if (!window.confirm(`Unblock ${userSummary(user)}?`)) return;
    try {
      await userService.unblockUser(user.id);
      toast.success('User unblocked');
      loadUsers();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to unblock user');
    }
  };

  const closeBlockModal = () => { setShowBlockModal(false); setBlockReason(''); setSelectedUser(null); };
  const handleSearch = (e) => { setSearch(e.target.value); setPage(1); };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Users</h1>

      {/* Filters */}
      <div className="bg-kasi-800 border border-white/[0.05] rounded-xl p-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Search</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-slate-500">
                <Icon name="search" className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={search}
                onChange={handleSearch}
                placeholder="User ID, phone, or Telegram chat ID…"
                className={`${inputCls} pl-9`}
              />
            </div>
          </div>
          <div>
            <label className={labelCls}>Status</label>
            <select
              value={filterBlocked === null ? 'all' : filterBlocked ? 'blocked' : 'active'}
              onChange={(e) => {
                const v = e.target.value;
                setFilterBlocked(v === 'all' ? null : v === 'blocked');
                setPage(1);
              }}
              className={selectCls}
            >
              <option value="all">All Users</option>
              <option value="active">Active Only</option>
              <option value="blocked">Blocked Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className={tableCls}>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className={theadCls}>
              <tr>
                <th className={thCls}>ID</th>
                <th className={thCls}>Phone</th>
                <th className={thCls}>Telegram</th>
                <th className={thCls}>Balance</th>
                <th className={thCls}>Status</th>
                <th className={thCls}>Joined</th>
                <th className={thCls}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <SkeletonRows cols={7} rows={8} />
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-14 text-center text-slate-500 text-sm">
                    No users found
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className={trHoverCls}>
                    <td className={`${tdCls} font-mono text-xs text-slate-500`}>{user.id}</td>
                    <td className={tdCls}>{user.phone_number ?? '—'}</td>
                    <td className={`${tdCls} font-mono text-xs`}>{user.telegram_chat_id ?? '—'}</td>
                    <td className={`${tdCls} text-amber-400 font-medium`}>
                      R {user.wallet_balance.toFixed(2)}
                    </td>
                    <td className={tdCls}>
                      <Badge status={user.is_blocked ? 'blocked' : 'active'} />
                    </td>
                    <td className={`${tdCls} text-slate-500`}>
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className={tdCls}>
                      {user.is_blocked ? (
                        <button
                          onClick={() => handleUnblock(user)}
                          className="text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors cursor-pointer"
                        >
                          Unblock
                        </button>
                      ) : (
                        <button
                          onClick={() => { setSelectedUser(user); setShowBlockModal(true); }}
                          className="text-xs font-medium text-red-400 hover:text-red-300 transition-colors cursor-pointer"
                        >
                          Block
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <Pagination
          page={page}
          totalPages={totalPages}
          total={total}
          pageSize={pageSize}
          onPage={setPage}
        />
      </div>

      {/* Block modal */}
      <Modal open={showBlockModal} onClose={closeBlockModal} title="Block User">
        <p className="text-sm text-slate-400 mb-4">
          You are about to block <span className="text-white font-medium">{userSummary(selectedUser)}</span>.
        </p>
        <div className="mb-5">
          <label className={labelCls}>
            Reason <span className="text-red-400">*</span>
          </label>
          <textarea
            value={blockReason}
            onChange={(e) => setBlockReason(e.target.value)}
            placeholder="Enter reason for blocking this user…"
            rows={3}
            className={textareaCls}
          />
        </div>
        <div className="flex justify-end gap-3">
          <button onClick={closeBlockModal} className={btnSecondary}>Cancel</button>
          <button onClick={handleBlock} className={btnDanger}>Block User</button>
        </div>
      </Modal>
    </div>
  );
};

export default Users;
