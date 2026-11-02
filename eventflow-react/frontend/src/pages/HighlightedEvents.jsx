import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import NavBar from "../components/NavBar";
import EventCard from "../components/EventCard";
import { getHighlightedEvents } from "../api/events";

export default function HighlightedEvents() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryPage = parseInt(searchParams.get("page") || "1", 10);

  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [count, setCount] = useState(0);

  useEffect(() => {
    async function fetchHighlights() {
      setLoading(true);
      setError(null);
      try {
        const data = await getHighlightedEvents({ page: queryPage });
        setEvents(data.results);
        setCount(data.count);
      } catch (err) {
        setError("Erro ao carregar eventos em destaque.");
      } finally {
        setLoading(false);
      }
    }
    fetchHighlights();
  }, [queryPage]);

  const handlePageChange = (newPage) => {
    if (newPage > 1) {
      setSearchParams({ page: newPage });
    } else {
      setSearchParams({});
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const totalPages = Math.ceil(count / 12);

  return (
    <div>
      <NavBar />
      
      <main className="container py-5">
        <h1 style={{ fontSize: "28px", fontWeight: "800", marginBottom: "8px" }}>
          🔥 Eventos em Destaque do Mês
        </h1>
        <p className="text-muted" style={{ marginBottom: "32px" }}>
          Confira a lista dos eventos mais populares e com maior adesão dos participantes.
        </p>

        {error && <div className="alert alert-danger">{error}</div>}

        {loading ? (
          <div className="text-center" style={{ color: "var(--text-muted)", padding: "40px" }}>
            Carregando destaques...
          </div>
        ) : events.length > 0 ? (
          <>
            <div className="event-grid">
              {events.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>

            {/* Barra de Paginação */}
            {totalPages > 1 && (
              <div className="pagination-container">
                <button
                  type="button"
                  onClick={() => handlePageChange(queryPage - 1)}
                  disabled={queryPage <= 1}
                  className="page-btn"
                >
                  ‹ Anterior
                </button>
                
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => handlePageChange(p)}
                    className={`page-btn ${p === queryPage ? "active" : ""}`}
                  >
                    {p}
                  </button>
                ))}

                <button
                  type="button"
                  onClick={() => handlePageChange(queryPage + 1)}
                  disabled={queryPage >= totalPages}
                  className="page-btn"
                >
                  Próximo ›
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center text-muted" style={{ padding: "40px" }}>
            Nenhum evento em destaque encontrado no momento.
          </div>
        )}
      </main>
    </div>
  );
}
