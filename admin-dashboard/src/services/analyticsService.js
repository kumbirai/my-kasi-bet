import api from './api';

export const analyticsService = {
  getDashboardStats: async () => {
    const response = await api.get('/api/admin/analytics/dashboard');
    return response.data;
  },

  getRevenueBreakdown: async (dateFrom, dateTo) => {
    const params = {};
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;
    const response = await api.get('/api/admin/analytics/revenue', { params });
    return response.data;
  },

  getUserEngagement: async () => {
    const response = await api.get('/api/admin/analytics/users');
    return response.data;
  },
};
