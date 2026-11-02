import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_URL !== undefined 
  ? import.meta.env.VITE_API_URL 
  : "";

// Ler cookies para obter csrftoken
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export function getCSRFToken() {
  return getCookie("eventflow_react_csrftoken") || getCookie("csrftoken");
}

export const api = axios.create({
  baseURL: API_BASE ? `${API_BASE}/api/` : "/api/",
  withCredentials: true, // Importante para trafegar cookies de sessão
});

api.interceptors.request.use((config) => {
  const token = getCSRFToken();
  if (token) {
    config.headers["X-CSRFToken"] = token;
  }
  return config;
});
