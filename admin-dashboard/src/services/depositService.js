import api from './api';

export const depositService = {
  getPendingDeposits: async () => {
    const response = await api.get('/api/admin/deposits/pending');
    return response.data;
  },

  getDeposits: async (page = 1, pageSize = 50, status = null, paymentMethod = null) => {
    const params = { page, page_size: pageSize };
    if (status) params.status = status;
    if (paymentMethod) params.payment_method = paymentMethod;
    const response = await api.get('/api/admin/deposits', { params });
    return response.data;
  },

  approveDeposit: async (depositId) => {
    const response = await api.post('/api/admin/deposits/approve', {
      deposit_id: depositId,
    });
    return response.data;
  },

  rejectDeposit: async (depositId, rejectionReason) => {
    const response = await api.post('/api/admin/deposits/reject', {
      deposit_id: depositId,
      rejection_reason: rejectionReason,
    });
    return response.data;
  },

  createDeposit: async (depositData) => {
    const response = await api.post('/api/admin/deposits', depositData);
    return response.data;
  },
};
