import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import NavBar from "../components/NavBar";
import EventCard from "../components/EventCard";
import { getMyRegistrations } from "../api/events";

export default function MyRegistrations() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadRegistrations() {
      try {
        const data = await getMyRegistrations();
        setEvents(data);
      } catch (err) {
        setError("Erro ao carregar suas inscrições.");
      } finally {
        setLoading(false);
      }
    }
    loadRegistrations();
  }, []);

  return (
    <div>
      <NavBar />
      
      <main className="container py-5">
        <h1 className="mb-4" style={{ fontSize: "28px", fontWeight: "800" }}>🎟️ Minhas Inscrições</h1>
        <p className="text-muted" style={{ marginBottom: "32px", marginTop: "-16px" }}>
          Aqui você acompanha todos os eventos em que garantiu sua vaga.
        </p>

        {loading ? (
          <div className="text-center" style={{ color: "var(--text-muted)", fontWeight: "500" }}>
            Carregando suas inscrições...
          </div>
        ) : error ? (
          <div className="alert alert-danger text-center">
            {error}
          </div>
        ) : events.length > 0 ? (
          <div className="event-grid">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        ) : (
          <div className="text-center" style={{ padding: "60px 0", border: "1px dashed var(--border)", borderRadius: "var(--radius-lg)", background: "var(--surface)" }}>
            <p className="text-muted" style={{ fontSize: "16px", marginBottom: "16px" }}>
              Você ainda não se inscreveu em nenhum evento.
            </p>
            <Link to="/" className="btn btn-primary">
              Explorar Eventos
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
