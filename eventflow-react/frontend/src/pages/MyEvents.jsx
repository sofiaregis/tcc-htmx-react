import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import NavBar from "../components/NavBar";
import MetricCard from "../components/MetricCard";
import { getMyEvents, getDashboardStats, deleteEvent } from "../api/events";
import { CATEGORIES } from "../components/EventCard";

export default function MyEvents() {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({ total_events: 0, total_registrations: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    try {
      const [eventsData, statsData] = await Promise.all([
        getMyEvents(),
        getDashboardStats(),
      ]);
      setEvents(eventsData);
      setStats(statsData);
    } catch (err) {
      setError("Erro ao carregar dados do painel.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("⚠️ Tem certeza que deseja deletar este evento permanentemente?")) return;

    try {
      await deleteEvent(id);
      // Recarregar os dados localmente
      setEvents((prev) => prev.filter((e) => e.id !== id));
      setStats((prev) => ({
        ...prev,
        total_events: prev.total_events - 1,
      }));
    } catch (err) {
      alert("Erro ao deletar o evento.");
    }
  };

  return (
    <div>
      <NavBar />
      
      <main className="container py-5">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
          <div>
            <h1 style={{ fontSize: "28px", fontWeight: "800" }}>💼 Painel de Eventos</h1>
            <p className="text-muted">Gerencie as atividades, inscritos e informações dos seus eventos.</p>
          </div>
          <Link to="/events/create/" className="btn btn-primary">
            + Criar Novo Evento
          </Link>
        </div>

        {loading ? (
          <div className="text-center" style={{ color: "var(--text-muted)", fontWeight: "500" }}>
            Carregando painel do organizador...
          </div>
        ) : error ? (
          <div className="alert alert-danger text-center">
            {error}
          </div>
        ) : (
          <>
            {/* Seção de Métricas */}
            <div className="dashboard-grid">
              <MetricCard 
                title="Eventos Organizados" 
                value={stats.total_events} 
                icon="📅"
              />
              <MetricCard 
                title="Total de Inscritos Geral" 
                value={stats.total_registrations} 
                icon="👥"
              />
            </div>

            {/* Listagem em Tabela */}
            <h2 className="section-title" style={{ fontSize: "20px", marginTop: "40px" }}>
              Meus Eventos Criados
            </h2>
            
            {events.length > 0 ? (
              <div className="table-responsive">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Evento</th>
                      <th>Data / Hora</th>
                      <th>Categoria</th>
                      <th>Inscritos</th>
                      <th style={{ textAlign: "right" }}>Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {events.map((event) => (
                      <tr key={event.id}>
                        <td>
                          <Link to={`/event/${event.id}/`} style={{ fontWeight: "700", color: "var(--text)" }}>
                            {event.title}
                          </Link>
                          <div className="text-muted" style={{ fontSize: "12px", marginTop: "4px" }}>
                            📍 {event.location}
                          </div>
                        </td>
                        <td>
                          <div style={{ fontWeight: "500" }}>
                            {new Date(event.date + "T00:00:00").toLocaleDateString("pt-BR")}
                          </div>
                          <div className="text-muted" style={{ fontSize: "12px" }}>
                            {event.time.substring(0, 5)}h
                          </div>
                        </td>
                        <td>
                          <span className="badge badge-primary">
                            {CATEGORIES[event.category] || event.category}
                          </span>
                        </td>
                        <td>
                          <span style={{ fontWeight: "700", color: "var(--primary)" }}>
                            {event.registrations_count}
                          </span>
                        </td>
                        <td>
                          <div className="table-actions" style={{ justifyContent: "flex-end" }}>
                            <Link to={`/event/${event.id}/registrations/`} className="btn btn-sm btn-secondary">
                              Inscritos
                            </Link>
                            <Link to={`/event/${event.id}/edit/`} className="btn btn-sm btn-outline">
                              Editar
                            </Link>
                            <button onClick={() => handleDelete(event.id)} className="btn btn-sm btn-danger">
                              Excluir
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center" style={{ padding: "60px 0", border: "1px dashed var(--border)", borderRadius: "var(--radius-lg)", background: "var(--surface)" }}>
                <p className="text-muted" style={{ fontSize: "16px", marginBottom: "16px" }}>
                  Você ainda não criou nenhum evento.
                </p>
                <Link to="/events/create/" className="btn btn-primary">
                  Criar Primeiro Evento
                </Link>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
