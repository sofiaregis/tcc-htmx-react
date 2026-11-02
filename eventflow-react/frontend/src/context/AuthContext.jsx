import { createContext, useState, useEffect } from "react";
import { api } from "../api/csrf";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Buscar dados do usuário logado ao iniciar a aplicação (sessão via cookie)
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await api.get("users/me/");
        setUser(res.data);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  const login = async (username, password) => {
    try {
      await api.post("users/login/", { username, password });
      const res = await api.get("users/me/");
      setUser(res.data);
      return { success: true };
    } catch (error) {
      console.error("Erro ao realizar login:", error.response?.data || error);
      return { success: false, error: error.response?.data?.error || "Credenciais inválidas." };
    }
  };

  const logout = async () => {
    try {
      await api.post("users/logout/");
    } catch (e) {
      console.warn("Erro ao fazer logout", e);
    } finally {
      setUser(null);
    }
  };

  const register = async (username, email, password) => {
    try {
      await api.post("users/register/", { username, email, password });
      const res = await api.get("users/me/");
      setUser(res.data);
      return { success: true };
    } catch (error) {
      console.error("Erro ao registrar usuário:", error.response?.data || error);
      return { success: false, error: error.response?.data?.error || "Erro ao registrar usuário." };
    }
  };

  const contextData = { user, login, logout, register, loading };

  return (
    <AuthContext.Provider value={contextData}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
