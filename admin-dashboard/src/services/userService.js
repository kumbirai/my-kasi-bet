import api from './api';

export const userService = {
  getUsers: async (page = 1, pageSize = 50, search = null, isBlocked = null) => {
    const params = { page, page_size: pageSize };
    if (search) params.search = search;
    if (isBlocked !== null) params.is_blocked = isBlocked;
    const response = await api.get('/api/admin/users', { params });
    return response.data;
  },

  getUserDetails: async (userId) => {
    const response = await api.get(`/api/admin/users/${userId}`);
    return response.data;
  },

  blockUser: async (userId, reason) => {
    const response = await api.post(`/api/admin/users/${userId}/block`, { reason });
    return response.data;
  },

  unblockUser: async (userId) => {
    const response = await api.post(`/api/admin/users/${userId}/unblock`);
    return response.data;
  },
};
