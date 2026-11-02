import { Link } from "react-router-dom";
import { API_BASE } from "../api/csrf";

export const CATEGORIES = {
  tech: "Tecnologia",
  business: "Negócios",
  art: "Artes",
  sports: "Esportes",
  music: "Música",
  education: "Educação",
  health: "Saúde e Bem-estar",
  food: "Culinária",
  environment: "Meio Ambiente",
  photography: "Fotografia",
  other: "Outros",
};

export default function EventCard({ event }) {
  // Trata a URL da imagem. Se for relativa, adiciona o host do backend.
  const imageUrl = event.image
    ? event.image.startsWith("http")
      ? event.image
      : `${API_BASE}${event.image}`
    : "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=500&auto=format&fit=crop&q=60"; // fallback image

  const rawDate = new Date(event.date + "T00:00:00").toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });

  const formattedDate = rawDate.replace(/ de ([a-z])/g, (m, p1) => ` de ${p1.toUpperCase()}`);

  // Limpa os segundos do formato de hora do Django (ex: "19:00:00" -> "19:00")
  const formattedTime = event.time ? event.time.substring(0, 5) : "";

  return (
    <div className={`event-card ${event.is_past ? "past" : ""}`}>
      {event.is_past && <div className="event-card-ended-badge">Encerrado</div>}
      <img src={imageUrl} alt={event.title} className="event-card-image" />
      
      <div className="event-card-content">
        <span className="event-card-category">
          {CATEGORIES[event.category] || event.category}
        </span>
        
        <h3 className="event-card-title">{event.title}</h3>
        
        <div className="event-card-meta">
          📅 {formattedDate} às {formattedTime}h
        </div>
        
        <div className="event-card-meta">
          📍 {event.location}
        </div>
        
        <div className="event-card-footer">
          <Link to={`/event/${event.id}/`} className="btn btn-sm btn-outline" style={{ width: "100%", justifyContent: "center" }}>
            Ver Detalhes
          </Link>
        </div>
      </div>
    </div>
  );
}
