import { useContext } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import AuthContext from "../context/AuthContext";

export default function NavBar() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const path = location.pathname;
  const isEventsActive = path === "/" || path.startsWith("/search") || path.startsWith("/events/highlighted") || path.startsWith("/events/today");
  const isMyRegistrationsActive = path.startsWith("/registrations/me");
  const isOrganizerActive = path.startsWith("/events/me") || path.startsWith("/events/create") || (path.startsWith("/event/") && (path.includes("/edit") || path.includes("/registrations")));
  const isLoginActive = path.startsWith("/users/login");

  return (
    <nav className="navbar">
      <div className="container navbar-container">
        <Link to="/" className="logo">
          ⚡ Event<span>Flow</span>
        </Link>

        <div className="nav-links">
          <Link to="/" className={`nav-link ${isEventsActive ? "active" : ""}`}>
            Eventos
          </Link>

          {user ? (
            <>
              <Link 
                to="/registrations/me/" 
                className={`nav-link ${isMyRegistrationsActive ? "active" : ""}`}
              >
                Minhas Inscrições
              </Link>
              <Link 
                to="/events/me/" 
                className={`nav-link ${isOrganizerActive ? "active" : ""}`}
              >
                Painel do Organizador
              </Link>
              <span className="text-muted" style={{ fontSize: "14px", fontWeight: "500", marginLeft: "8px" }}>
                Olá, <strong>{user.username}</strong>
              </span>
              <button onClick={handleLogout} className="btn btn-sm btn-outline">
                Sair
              </button>
            </>
          ) : (
            <>
              <Link to="/users/login/" className={`nav-link ${isLoginActive ? "active" : ""}`}>
                Entrar
              </Link>
              <Link to="/users/register/" className="btn btn-sm btn-primary">
                Cadastrar-se
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
