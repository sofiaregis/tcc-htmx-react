import { useEffect, useState, useRef, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import NavBar from "../components/NavBar";
import EventCard, { CATEGORIES } from "../components/EventCard";
import { getEvents } from "../api/events";

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Extrai filtros iniciais da URL
  const queryQ = searchParams.get("q") || "";
  const queryCategory = searchParams.get("category") || "";

  const [searchTerm, setSearchTerm] = useState(queryQ);
  const [categoryTerm, setCategoryTerm] = useState(queryCategory);
  
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const sentinelRef = useRef(null);

  // Executa busca da página 1 quando os parâmetros da URL mudam
  useEffect(() => {
    async function fetchInitialResults() {
      setLoading(true);
      setError(null);
      setPage(1);
      setEvents([]);
      setHasMore(true);

      try {
        const params = {};
        const q = searchParams.get("q");
        const cat = searchParams.get("category");
        
        if (q) params.search = q;
        if (cat) params.category = cat;
        params.page = 1;

        const data = await getEvents(params);
        setEvents(data.results || []);
        setCount(data.count || 0);
        setHasMore(Boolean(data.next));
      } catch (err) {
        setError("Ocorreu um erro ao carregar os resultados da busca.");
      } finally {
        setLoading(false);
      }
    }
    fetchInitialResults();
  }, [searchParams]);

  // Função para carregar próxima página via Infinite Scroll
  const fetchNextPage = useCallback(async () => {
    if (loadingMore || !hasMore) return;

    setLoadingMore(true);
    try {
      const nextPage = page + 1;
      const params = {};
      const q = searchParams.get("q");
      const cat = searchParams.get("category");
      
      if (q) params.search = q;
      if (cat) params.category = cat;
      params.page = nextPage;

      const data = await getEvents(params);
      const newResults = data.results || [];
      
      setEvents((prev) => [...prev, ...newResults]);
      setPage(nextPage);
      setHasMore(Boolean(data.next));
    } catch (err) {
      console.error("Erro ao carregar mais eventos:", err);
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, hasMore, page, searchParams]);

  // Observer para rolar a página e detectar quando o elemento final entra em tela
  useEffect(() => {
    if (loading || !hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loadingMore) {
          fetchNextPage();
        }
      },
      { rootMargin: "400px", threshold: 0.1 }
    );

    const currentSentinel = sentinelRef.current;
    if (currentSentinel) {
      observer.observe(currentSentinel);
    }

    return () => {
      if (currentSentinel) {
        observer.unobserve(currentSentinel);
      }
    };
  }, [loading, hasMore, loadingMore, fetchNextPage]);

  // Atualiza URL com novos termos ao enviar o form e reseta filtros
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const newParams = {};
    if (searchTerm.trim()) newParams.q = searchTerm;
    if (categoryTerm) newParams.category = categoryTerm;
    setSearchParams(newParams);
  };

  return (
    <div>
      <NavBar />
      
      <main className="container py-5">
        <h1 style={{ fontSize: "28px", fontWeight: "800", marginBottom: "24px" }}>
          🔍 Busca de Eventos
        </h1>

        {/* Formulário de Busca e Filtros */}
        <form onSubmit={handleSearchSubmit} className="search-filter-container" style={{ margin: "0 0 40px 0", maxWidth: "100%" }}>
          <div className="search-input-wrapper">
            <input
              type="text"
              placeholder="Digite o título ou palavras-chave..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          <select
            value={categoryTerm}
            onChange={(e) => setCategoryTerm(e.target.value)}
            className="filter-select"
          >
            <option value="">Todas as Categorias</option>
            {Object.entries(CATEGORIES).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
          <button type="submit" className="btn btn-primary">
            Buscar
          </button>
        </form>

        {/* Resultados */}
        <section>
          {loading ? (
            <div className="text-center" style={{ padding: "60px 0", color: "var(--text-muted)", fontWeight: "500" }}>
              Carregando resultados...
            </div>
          ) : error ? (
            <div className="alert alert-danger text-center">
              {error}
            </div>
          ) : events.length > 0 ? (
            <>
              <p className="text-muted" style={{ marginBottom: "24px" }}>
                Encontramos <strong>{count}</strong> evento(s) correspondente(s).
              </p>
              <div className="event-grid">
                {events.map((event) => (
                  <EventCard key={event.id} event={event} />
                ))}
              </div>

              {/* Sentinela de Infinite Scroll */}
              <div ref={sentinelRef} style={{ height: "40px", marginTop: "20px", display: "flex", justifyContent: "center", alignItems: "center" }}>
                {loadingMore && (
                  <span className="text-muted" style={{ fontSize: "14px", fontWeight: "600" }}>
                    Carregando mais eventos...
                  </span>
                )}
              </div>
            </>
          ) : (
            <div className="text-center" style={{ padding: "80px 0", border: "1px dashed var(--border)", borderRadius: "var(--radius-lg)", background: "var(--surface)" }}>
              <p className="text-muted" style={{ fontSize: "16px", marginBottom: "16px" }}>
                Nenhum evento correspondente encontrado.
              </p>
              <button 
                type="button" 
                onClick={() => { setSearchTerm(""); setCategoryTerm(""); setSearchParams({}); }} 
                className="btn btn-sm btn-secondary"
              >
                Limpar Filtros
              </button>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
