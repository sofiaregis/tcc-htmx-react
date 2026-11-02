import { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import NavBar from "../components/NavBar";
import EventCard from "../components/EventCard";
import Carousel from "../components/Carousel";
import { getHighlightedEvents, getTodayEvents } from "../api/events";

const CATEGORY_ITEMS = [
  { key: "tech", label: "Tecnologia", icon: "💻" },
  { key: "business", label: "Negócios", icon: "📈" },
  { key: "art", label: "Artes", icon: "🎨" },
  { key: "sports", label: "Esportes", icon: "⚽" },
  { key: "music", label: "Música", icon: "🎵" },
  { key: "education", label: "Educação", icon: "🎓" },
  { key: "health", label: "Saúde", icon: "🧘" },
  { key: "food", label: "Culinária", icon: "🍳" },
  { key: "environment", label: "Meio Ambiente", icon: "🌱" },
  { key: "photography", label: "Fotografia", icon: "📷" },
  { key: "other", label: "Outros", icon: "✨" },
];

export default function Home() {
  const navigate = useNavigate();
  const location = useLocation();
  const [message, setMessage] = useState(location.state?.message || null);
  const [highlights, setHighlights] = useState([]);
  const [todayEvents, setTodayEvents] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  // Limpa o state de navegação para evitar persistência no reload
  useEffect(() => {
    if (location.state?.message) {
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location, navigate]);

  // Carregar destaques (limite 10) e hoje (limite 10)
  useEffect(() => {
    async function loadCarouselsData() {
      try {
        const [highlightedData, todayData] = await Promise.all([
          getHighlightedEvents({ limit: 10 }),
          getTodayEvents({ limit: 10 }),
        ]);
        setHighlights(highlightedData);
        setTodayEvents(todayData);
      } catch (err) {
        console.error("Erro ao carregar dados dos carrosséis:", err);
      } finally {
        setLoading(false);
      }
    }
    loadCarouselsData();
  }, []);

  // Handler de envio de busca
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search/?q=${encodeURIComponent(searchQuery)}`);
    } else {
      navigate("/search/");
    }
  };

  return (
    <div>
      <NavBar />
      
      {message && (
        <div className="container" style={{ marginTop: "24px" }}>
          <div className="alert alert-success">
            {message}
          </div>
        </div>
      )}
      
      {/* Hero Section */}
      <header className="hero">
        <div className="container">
          <h1>Descubra Eventos Incríveis</h1>
          <p>Explore, participe e organize conferências, workshops e encontros locais com facilidade e segurança.</p>
        </div>
      </header>

      {/* Barra de Busca Redirecionada */}
      <div className="container">
        <form onSubmit={handleSearchSubmit} className="search-filter-container">
          <div className="search-input-wrapper">
            <input
              type="text"
              placeholder="Pesquise por nome, palavras-chave..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Buscar
          </button>
        </form>
      </div>

      <main className="container py-5" style={{ paddingTop: 0 }}>
        {loading ? (
          <div className="text-center" style={{ padding: "60px 0", color: "var(--text-muted)", fontWeight: "500" }}>
            Carregando eventos...
          </div>
        ) : (
          <>
            {/* 1. Carrossel: Eventos mais Inscritos deste Mês */}
            {highlights.length > 0 && (
              <section className="mb-4" style={{ marginBottom: "56px" }}>
                <div className="section-header">
                  <h2 className="section-title">🔥 Mais Inscritos do Mês</h2>
                  <Link to="/events/highlighted/" className="view-all-link">
                    Ver todos →
                  </Link>
                </div>
                <Carousel>
                  {highlights.map((event) => (
                    <div key={event.id} className="carousel-item-wrapper">
                      <EventCard event={event} />
                    </div>
                  ))}
                </Carousel>
              </section>
            )}

            {/* 2. Carrossel: Explore nossas Categorias */}
            <section className="mb-4" style={{ marginBottom: "56px" }}>
              <div className="section-header">
                <h2 className="section-title"> Explore Categorias</h2>
              </div>
              <Carousel>
                {CATEGORY_ITEMS.map((item) => (
                  <div
                    key={item.key}
                    onClick={() => navigate(`/search/?category=${item.key}`)}
                    className="category-carousel-card"
                  >
                    <span className="category-icon">{item.icon}</span>
                    <span>{item.label}</span>
                  </div>
                ))}
              </Carousel>
            </section>

            {/* 3. Carrossel: O que fazer Hoje */}
            {todayEvents.length > 0 && (
              <section className="mb-4" style={{ marginBottom: "56px" }}>
                <div className="section-header">
                  <h2 className="section-title">📅 Acontecendo Hoje</h2>
                  <Link to="/events/today/" className="view-all-link">
                    Ver todos →
                  </Link>
                </div>
                <Carousel>
                  {todayEvents.map((event) => (
                    <div key={event.id} className="carousel-item-wrapper">
                      <EventCard event={event} />
                    </div>
                  ))}
                </Carousel>
              </section>
            )}

            {/* CTA Final: Ver todos os eventos cadastrados */}
            <section style={{ textAlign: "center", padding: "48px 24px", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)", background: "var(--surface)", marginTop: "40px" }}>
              <h3 style={{ fontSize: "20px", fontWeight: "700", marginBottom: "8px" }}>
                Quer explorar mais opções?
              </h3>
              <p className="text-muted" style={{ marginBottom: "20px", fontSize: "15px" }}>
                Acesse a nossa listagem completa para visualizar todos os eventos cadastrados na plataforma.
              </p>
              <Link to="/search/" className="btn btn-secondary">
                🔍 Ver Todos os Eventos
              </Link>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
