import { useState, useEffect } from "react";
import { CATEGORIES } from "./EventCard";

export default function EventForm({ initialData = null, onSubmit, buttonText = "Salvar Evento", loading = false }) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    location: "",
    date: "",
    time: "",
    category: "other",
  });
  const [imageFile, setImageFile] = useState(null);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (initialData) {
      // Ajusta hora de HH:MM:SS para HH:MM para coincidir com o input type="time"
      const formattedTime = initialData.time ? initialData.time.substring(0, 5) : "";
      setFormData({
        title: initialData.title || "",
        description: initialData.description || "",
        location: initialData.location || "",
        date: initialData.date || "",
        time: formattedTime,
        category: initialData.category || "other",
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Limpa erro ao digitar
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0]);
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.title.trim()) newErrors.title = "O título é obrigatório.";
    if (!formData.description.trim()) newErrors.description = "A descrição é obrigatória.";
    if (!formData.location.trim()) newErrors.location = "O local é obrigatório.";
    if (!formData.date) newErrors.date = "A data é obrigatória.";
    if (!formData.time) newErrors.time = "O horário é obrigatório.";
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    // Constrói o FormData para envio de multipart/form-data
    const dataToSend = new FormData();
    dataToSend.append("title", formData.title);
    dataToSend.append("description", formData.description);
    dataToSend.append("location", formData.location);
    dataToSend.append("date", formData.date);
    dataToSend.append("time", formData.time);
    dataToSend.append("category", formData.category);
    
    if (imageFile) {
      dataToSend.append("image", imageFile);
    }

    onSubmit(dataToSend);
  };

  return (
    <form onSubmit={handleSubmit} className="event-form" style={{ background: "var(--surface)", padding: "32px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", boxShadow: "var(--shadow)" }}>
      <div className="form-group">
        <label className="form-label">Título do Evento *</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className="form-input"
          placeholder="Ex: Workshop Avançado de JavaScript"
        />
        {errors.title && <div className="form-error">⚠️ {errors.title}</div>}
      </div>

      <div className="form-group">
        <label className="form-label">Categoria *</label>
        <select
          name="category"
          value={formData.category}
          onChange={handleChange}
          className="filter-select"
          style={{ width: "100%" }}
        >
          {Object.entries(CATEGORIES).map(([key, label]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label className="form-label">Descrição *</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          className="form-textarea"
          rows="5"
          placeholder="Diga aos participantes o que acontecerá no evento..."
        ></textarea>
        {errors.description && <div className="form-error">⚠️ {errors.description}</div>}
      </div>

      <div className="form-group" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
        <div>
          <label className="form-label">Data *</label>
          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            className="form-input"
          />
          {errors.date && <div className="form-error">⚠️ {errors.date}</div>}
        </div>
        <div>
          <label className="form-label">Horário *</label>
          <input
            type="time"
            name="time"
            value={formData.time}
            onChange={handleChange}
            className="form-input"
          />
          {errors.time && <div className="form-error">⚠️ {errors.time}</div>}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">Local *</label>
        <input
          type="text"
          name="location"
          value={formData.location}
          onChange={handleChange}
          className="form-input"
          placeholder="Ex: Auditório B - UFSC ou Online"
        />
        {errors.location && <div className="form-error">⚠️ {errors.location}</div>}
      </div>

      <div className="form-group">
        <label className="form-label">Imagem de Capa</label>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="form-input"
          style={{ padding: "8px" }}
        />
        <small className="text-muted" style={{ display: "block", marginTop: "4px" }}>
          Deixe vazio para manter a imagem atual ou usar a capa padrão.
        </small>
      </div>

      <button type="submit" disabled={loading} className="btn btn-primary" style={{ width: "100%", marginTop: "16px" }}>
        {loading ? "Processando..." : buttonText}
      </button>
    </form>
  );
}
