import { useState, useContext, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthContext from "../context/AuthContext";
import NavBar from "../components/NavBar";

export default function Register() {
  const { register, user } = useContext(AuthContext);
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [registered, setRegistered] = useState(false);
  
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  // Redireciona se o usuário já estiver logado
  useEffect(() => {
    if (user && !registered) {
      navigate("/");
    }
  }, [user, navigate, registered]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!username.trim() || !email.trim() || !password.trim()) {
      setError("Por favor, preencha todos os campos obrigatórios.");
      return;
    }

    if (password !== confirmPassword) {
      setError("As senhas não coincidem.");
      return;
    }

    setLoading(true);
    const result = await register(username, email, password);
    setLoading(false);

    if (result.success) {
      setRegistered(true);
      navigate("/", { state: { message: "Cadastro realizado com sucesso! Bem-vindo ao EventFlow." } });
    } else {
      setError(result.error || "Ocorreu um erro ao criar a conta. Tente outro nome de usuário.");
    }
  };

  return (
    <div>
      <NavBar />
      
      <main className="container">
        <div className="auth-container">
          <h1 className="auth-title">Criar Conta</h1>
          <p className="auth-subtitle">Registre-se no EventFlow para poder criar seus próprios eventos e se inscrever.</p>

          {error && <div className="alert alert-danger">⚠️ {error}</div>}
          {success && <div className="alert alert-success">✓ {success}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Nome de Usuário *</label>
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
              <label className="form-label">Endereço de E-mail *</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="form-input"
                placeholder="Ex: sofia@ufsc.br"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Senha *</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="form-input"
                placeholder="Mínimo 6 caracteres"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Confirmar Senha *</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="form-input"
                placeholder="Digite a senha novamente"
                required
              />
            </div>

            <button type="submit" disabled={loading || success} className="btn btn-primary" style={{ width: "100%", marginTop: "12px" }}>
              {loading ? "Criando Conta..." : "Registrar Conta"}
            </button>
          </form>

          <div style={{ marginTop: "24px", textAlign: "center", fontSize: "14px" }}>
            Já tem uma conta? <Link to="/users/login/">Entrar na conta</Link>
          </div>
        </div>
      </main>
    </div>
  );
}
