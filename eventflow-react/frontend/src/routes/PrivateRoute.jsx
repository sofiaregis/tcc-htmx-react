import { useContext } from "react";
import { Navigate, useLocation } from "react-router-dom";
import AuthContext from "../context/AuthContext";

export default function PrivateRoute({ children }) {
  const { user, loading } = useContext(AuthContext);
  const location = useLocation();

  if (loading) {
    return (
      <div className="text-center" style={{ padding: "100px 0", color: "var(--text-muted)", fontWeight: "500" }}>
        Autenticando...
      </div>
    );
  }

  if (!user) {
    // Redireciona para o login salvando a página que o usuário tentou acessar
    return <Navigate to={`/users/login/?next=${encodeURIComponent(location.pathname)}`} replace />;
  }

  return children;
}
