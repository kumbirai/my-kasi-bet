import api from './api';

export const withdrawalService = {
  getPendingWithdrawals: async () => {
    const response = await api.get('/api/admin/withdrawals/pending');
    return response.data;
  },

  getWithdrawals: async (page = 1, pageSize = 50, status = null) => {
    const params = { page, page_size: pageSize };
    if (status) params.status = status;
    const response = await api.get('/api/admin/withdrawals', { params });
    return response.data;
  },

  approveWithdrawal: async (withdrawalId, paymentReference = null) => {
    const response = await api.post('/api/admin/withdrawals/approve', {
      withdrawal_id: withdrawalId,
      payment_reference: paymentReference,
    });
    return response.data;
  },

  rejectWithdrawal: async (withdrawalId, rejectionReason) => {
    const response = await api.post('/api/admin/withdrawals/reject', {
      withdrawal_id: withdrawalId,
      rejection_reason: rejectionReason,
    });
    return response.data;
  },
};
