import { useEffect, useState, useContext } from "react";
import { useParams, Link, useNavigate, useLocation } from "react-router-dom";
import AuthContext from "../context/AuthContext";
import { getEventDetails, registerForEvent, cancelRegistration, deleteEvent } from "../api/events";
import { CATEGORIES } from "../components/EventCard";
import { API_BASE } from "../api/csrf";
import NavBar from "../components/NavBar";

export default function EventDetails() {
  const { id } = useParams();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const fetchEvent = async () => {
    try {
      const data = await getEventDetails(id);
      setEvent(data);
      setError(null);
    } catch (err) {
      setError("Erro ao carregar os detalhes do evento.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvent();
  }, [id]);

  const handleRegister = async () => {
    if (!user) {
      // Redireciona para o login salvando a URL atual
      navigate(`/users/login/?next=${encodeURIComponent(location.pathname)}`);
      return;
    }

    setActionLoading(true);
    setSuccessMessage("");
    try {
      await registerForEvent(id);
      setSuccessMessage("Inscrição realizada com sucesso!");
      // Atualiza o estado do evento na tela
      setEvent((prev) => ({
        ...prev,
        is_registered: true,
        registrations_count: prev.registrations_count + 1,
      }));
    } catch (err) {
      const msg = err.response?.data?.detail || err.response?.data?.error || "Erro ao se inscrever.";
      alert(msg);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancelRegister = async () => {
    if (!window.confirm("Deseja realmente cancelar sua inscrição neste evento?")) return;

    setActionLoading(true);
    setSuccessMessage("");
    try {
      await cancelRegistration(id);
      setSuccessMessage("Inscrição cancelada com sucesso.");
      setEvent((prev) => ({
        ...prev,
        is_registered: false,
        registrations_count: Math.max(0, prev.registrations_count - 1),
      }));
    } catch (err) {
      alert("Erro ao cancelar inscrição. Tente novamente.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("⚠️ ATENÇÃO: Tem certeza que deseja excluir permanentemente este evento?")) return;

    setActionLoading(true);
    try {
      await deleteEvent(id);
      alert("Evento excluído com sucesso!");
      navigate("/events/me/");
    } catch (err) {
      alert("Erro ao excluir evento. Verifique se você possui permissão.");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div>
        <NavBar />
        <div className="container py-5 text-center" style={{ color: "var(--text-muted)", fontWeight: "500" }}>
          Carregando informações do evento...
        </div>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div>
        <NavBar />
        <div className="container py-5">
          <div className="alert alert-danger text-center">
            {error || "Evento não encontrado."}
          </div>
          <div className="text-center">
            <Link to="/" className="btn btn-outline">Voltar para a Home</Link>
          </div>
        </div>
      </div>
    );
  }

  const isOrganizer = user && event.organizer_username === user.username;
  
  const imageUrl = event.image
    ? event.image.startsWith("http")
      ? event.image
      : `${API_BASE}${event.image}`
    : "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=1000&auto=format&fit=crop&q=80";

  const rawDate = new Date(event.date + "T00:00:00").toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
  
  const formattedDate = rawDate.charAt(0).toUpperCase() + rawDate.slice(1).replace(/ de ([a-z])/g, (m, p1) => ` de ${p1.toUpperCase()}`);
  
  const formattedTime = event.time ? event.time.substring(0, 5) : "";

  return (
    <div>
      <NavBar />
      
      <main className="container py-5">
        
        {successMessage && (
          <div className="alert alert-success">
            ✨ {successMessage}
          </div>
        )}

        <div style={{ marginBottom: "20px" }}>
          <Link to="/" className="btn btn-sm btn-outline">
            ← Voltar para todos os eventos
          </Link>
        </div>

        <div className="event-details-layout">
          {/* Main Info */}
          <div className="event-details-main">
            <img src={imageUrl} alt={event.title} className="event-details-image" />
            
            <div className="event-details-body">
              <span className="badge badge-primary" style={{ marginBottom: "12px" }}>
                {CATEGORIES[event.category] || event.category}
              </span>
              
              <h1 className="event-details-title">{event.title}</h1>
              
              <div className="text-muted" style={{ fontSize: "14px", marginBottom: "24px" }}>
                Organizado por: <strong>@{event.organizer_username}</strong>
              </div>
              
              <h3 style={{ fontSize: "20px", fontWeight: "700", marginBottom: "12px", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>
                Sobre o Evento
              </h3>
              
              <p className="event-description">{event.description}</p>
            </div>
          </div>

          {/* Sidebar */}
          <div className="event-details-sidebar">
            {/* Tickets / Registration Action */}
            <div className="sidebar-card">
              <h3 className="sidebar-card-title">Participação</h3>
              
              <div style={{ marginBottom: "16px" }}>
                <div className="text-muted" style={{ fontSize: "13px", fontWeight: "600", textTransform: "uppercase" }}>
                  Inscritos no momento
                </div>
                <div style={{ fontSize: "28px", fontWeight: "800", color: "var(--primary)" }}>
                  {event.registrations_count}
                </div>
              </div>

              {event.is_past ? (
                <button className="btn btn-disabled" style={{ width: "100%" }} disabled>
                  Evento Encerrado
                </button>
              ) : isOrganizer ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  <div className="alert alert-success" style={{ padding: "10px", fontSize: "13px", marginBottom: 0 }}>
                    Você é o organizador deste evento.
                  </div>
                  <Link to={`/event/${event.id}/edit/`} className="btn btn-outline" style={{ justifyContent: "center" }}>
                    ✏️ Editar Evento
                  </Link>
                  <Link to={`/event/${event.id}/registrations/`} className="btn btn-secondary" style={{ justifyContent: "center" }}>
                    👥 Ver Lista de Inscritos
                  </Link>
                  <button onClick={handleDelete} className="btn btn-danger" style={{ width: "100%" }} disabled={actionLoading}>
                    🗑️ Excluir Evento
                  </button>
                </div>
              ) : event.is_registered ? (
                <div>
                  <div className="alert alert-success" style={{ padding: "10px", fontSize: "13px", marginBottom: "12px" }}>
                    ✓ Você está inscrito!
                  </div>
                  <button onClick={handleCancelRegister} className="btn btn-outline" style={{ width: "100%", color: "var(--danger)", borderColor: "var(--danger)" }} disabled={actionLoading}>
                    Cancelar Inscrição
                  </button>
                </div>
              ) : (
                <button onClick={handleRegister} className="btn btn-primary" style={{ width: "100%" }} disabled={actionLoading}>
                  {actionLoading ? "Processando..." : "Garantir Inscrição"}
                </button>
              )}
            </div>

            {/* Event Info Details */}
            <div className="sidebar-card">
              <h3 className="sidebar-card-title">Detalhes</h3>
              
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                <div>
                  <div style={{ fontWeight: "600", fontSize: "14px" }}>📅 Data do Evento</div>
                  <div className="text-muted" style={{ fontSize: "14px" }}>{formattedDate}</div>
                </div>
                <div>
                  <div style={{ fontWeight: "600", fontSize: "14px" }}>⏰ Horário</div>
                  <div className="text-muted" style={{ fontSize: "14px" }}>{formattedTime}h</div>
                </div>
                <div>
                  <div style={{ fontWeight: "600", fontSize: "14px" }}>📍 Local</div>
                  <div className="text-muted" style={{ fontSize: "14px" }}>{event.location}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
