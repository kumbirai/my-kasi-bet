import api from './api';

export const matchService = {
  getMatches: async (status = null) => {
    const params = {};
    if (status) params.status = status;
    const response = await api.get('/api/admin/matches', { params });
    return response.data;
  },

  createMatch: async (matchData) => {
    const response = await api.post('/api/admin/matches', matchData);
    return response.data;
  },

  settleMatch: async (matchId, result) => {
    const response = await api.post(`/api/admin/matches/${matchId}/settle`, {
      result,
    });
    return response.data;
  },
};
