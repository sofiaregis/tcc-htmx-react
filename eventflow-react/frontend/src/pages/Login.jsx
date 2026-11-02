import { useState, useContext, useEffect } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import AuthContext from "../context/AuthContext";
import NavBar from "../components/NavBar";

export default function Login() {
  const { login, user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Redireciona se o usuário já estiver logado previamente
  useEffect(() => {
    if (user) {
      const next = searchParams.get("next") || "/";
      navigate(next);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError("Por favor, preencha todos os campos.");
      return;
    }

    setLoading(true);
    setError("");
    
    const result = await login(username, password);
    setLoading(false);
    
    if (result.success) {
      const next = searchParams.get("next") || "/";
      navigate(next, { state: { message: `Bem-vindo de volta, ${username}!` } });
    } else {
      setError(result.error || "Credenciais inválidas");
    }
  };

  return (
    <div>
      <NavBar />
      
      <main className="container">
        <div className="auth-container">
          <h1 className="auth-title">Entrar no EventFlow</h1>
          <p className="auth-subtitle">Acesse sua conta para gerenciar e se inscrever em eventos.</p>

          {error && <div className="alert alert-danger">⚠️ {error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Nome de Usuário</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="form-input"
                placeholder="Ex: sofia_regis"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Senha</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                placeholder="Sua senha secreta"
                required
              />
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary" style={{ width: "100%", marginTop: "12px" }}>
              {loading ? "Entrando..." : "Acessar Conta"}
            </button>
          </form>

          <div style={{ marginTop: "24px", textAlign: "center", fontSize: "14px" }}>
            Não tem uma conta? <Link to="/users/register/">Cadastre-se aqui</Link>
          </div>
        </div>
      </main>
    </div>
  );
}
