import api from './api';

export const betService = {
  getBets: async (page = 1, pageSize = 50, filters = {}) => {
    const params = { page, page_size: pageSize };
    if (filters.bet_type) params.bet_type = filters.bet_type;
    if (filters.status) params.status = filters.status;
    if (filters.user_id) params.user_id = filters.user_id;
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;
    const response = await api.get('/api/admin/bets', { params });
    return response.data;
  },

  getActiveBets: async () => {
    const response = await api.get('/api/admin/bets/active');
    return response.data;
  },

  getBetStatistics: async (filters = {}) => {
    const params = {};
    if (filters.bet_type) params.bet_type = filters.bet_type;
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;
    const response = await api.get('/api/admin/bets/statistics', { params });
    return response.data;
  },
};
