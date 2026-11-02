import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import EventForm from "../components/EventForm";
import { getEventDetails, updateEvent } from "../api/events";

export default function EditEvent() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadEvent() {
      try {
        const data = await getEventDetails(id);
        setEvent(data);
      } catch (err) {
        setError("Erro ao carregar dados do evento.");
      } finally {
        setLoading(false);
      }
    }
    loadEvent();
  }, [id]);

  const handleSubmit = async (formData) => {
    setSaving(true);
    setError("");
    try {
      await updateEvent(id, formData);
      alert("Evento atualizado com sucesso!");
      navigate("/events/me/");
    } catch (err) {
      console.error("Erro ao salvar alterações:", err.response?.data || err);
      setError(
        err.response?.data?.error || 
        "Erro ao salvar as alterações. Verifique os campos."
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <NavBar />
      
      <main className="container py-5" style={{ maxWidth: "700px" }}>
        <h1 className="mb-4" style={{ fontSize: "28px", fontWeight: "800" }}>✏️ Editar Evento</h1>
        <p className="text-muted" style={{ marginBottom: "32px", marginTop: "-16px" }}>
          Altere as informações desejadas e salve as mudanças.
        </p>

        {error && <div className="alert alert-danger">⚠️ {error}</div>}

        {loading ? (
          <div className="text-center" style={{ color: "var(--text-muted)", padding: "40px" }}>
            Carregando informações do evento...
          </div>
        ) : (
          <EventForm 
            initialData={event} 
            onSubmit={handleSubmit} 
            buttonText="Salvar Alterações" 
            loading={saving} 
          />
        )}
      </main>
    </div>
  );
}
