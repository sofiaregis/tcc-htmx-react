import { api } from "./csrf";

export const getEvents = async (params = {}) => {
  const response = await api.get("/events/", { params });
  return response.data;
};

export const getEventDetails = async (id) => {
  const response = await api.get(`/events/${id}/`);
  return response.data;
};

export const createEvent = async (formData) => {
  const response = await api.post("/events/create/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const updateEvent = async (id, formData) => {
  const response = await api.patch(`/events/${id}/`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const deleteEvent = async (id) => {
  const response = await api.delete(`/events/${id}/`);
  return response.data;
};

export const registerForEvent = async (eventId) => {
  const response = await api.post(`/events/${eventId}/register/`);
  return response.data;
};

export const cancelRegistration = async (eventId) => {
  const response = await api.delete(`/events/${eventId}/register/`);
  return response.data;
};

export const getEventRegistrations = async (eventId) => {
  const response = await api.get(`/events/${eventId}/registrations/`);
  return response.data;
};

export const getMyRegistrations = async () => {
  const response = await api.get("/registrations/me/");
  return response.data;
};

export const getMyEvents = async () => {
  const response = await api.get("/events/me/");
  return response.data;
};

export const getDashboardStats = async () => {
  const response = await api.get("/events/dashboard-stats/");
  return response.data;
};

export const getHighlightedEvents = async (params = {}) => {
  const response = await api.get("/events/highlighted/", { params });
  return response.data;
};

export const getTodayEvents = async (params = {}) => {
  const response = await api.get("/events/today/", { params });
  return response.data;
};
