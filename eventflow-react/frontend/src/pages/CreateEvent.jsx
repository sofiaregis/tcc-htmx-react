import { useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/NavBar";
import EventForm from "../components/EventForm";
import { createEvent } from "../api/events";

export default function CreateEvent() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError("");
    try {
      await createEvent(formData);
      alert("Evento criado com sucesso!");
      navigate("/events/me/");
    } catch (err) {
      console.error("Erro ao criar evento:", err.response?.data || err);
      setError(
        err.response?.data?.error || 
        "Erro ao criar o evento. Por favor, verifique os campos."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <NavBar />
      
      <main className="container py-5" style={{ maxWidth: "700px" }}>
        <h1 className="mb-4" style={{ fontSize: "28px", fontWeight: "800" }}>➕ Novo Evento</h1>
        <p className="text-muted" style={{ marginBottom: "32px", marginTop: "-16px" }}>
          Preencha o formulário abaixo para registrar um novo evento na plataforma.
        </p>

        {error && <div className="alert alert-danger">⚠️ {error}</div>}

        <EventForm onSubmit={handleSubmit} buttonText="Publicar Evento" loading={loading} />
      </main>
    </div>
  );
}
