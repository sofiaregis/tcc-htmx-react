import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import NavBar from "../components/NavBar";
import { getEventRegistrations } from "../api/events";

export default function EventRegistrations() {
  const { id } = useParams();
  
  const [registrations, setRegistrations] = useState([]);
  const [eventTitle, setEventTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadRegistrations() {
      try {
        const data = await getEventRegistrations(id);
        setRegistrations(data.registrations || []);
        setEventTitle(data.event_title || "");
      } catch (err) {
        setError("Erro ao carregar a lista de inscritos.");
      } finally {
        setLoading(false);
      }
    }
    loadRegistrations();
  }, [id]);

  const handleExportCSV = () => {
    // Cabeçalho do CSV
    const header = "Nome,Email,Data de Inscricao\n";
    // Linhas formatadas
    const rows = registrations
      .map((r) => {
        const formattedDate = new Date(r.registered_at).toISOString().replace(/T/, ' ').replace(/\..+/, '');
        // Escapa possíveis vírgulas nos nomes
        const escapedName = r.name.includes(",") ? `"${r.name}"` : r.name;
        return `${escapedName},${r.email},${formattedDate}`;
      })
      .join("\n");
      
    const blob = new Blob([header + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `inscritos_${eventTitle.toLowerCase().replace(/\s+/g, '_')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      <NavBar />
      
      <main className="container py-5" style={{ maxWidth: "800px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
          <div>
            <h1 style={{ fontSize: "28px", fontWeight: "800" }}>👥 Lista de Inscritos</h1>
            <p className="text-muted">
              Visualização de participantes inscritos em: <strong>{eventTitle || "Carregando..."}</strong>
            </p>
          </div>
          {registrations.length > 0 && (
            <button onClick={handleExportCSV} className="btn btn-secondary" style={{ display: "inline-flex", alignItems: "center", gap: "8px", whiteSpace: "nowrap" }}>
              📥 Exportar CSV
            </button>
          )}
        </div>

        {error && <div className="alert alert-danger">⚠️ {error}</div>}

        {loading ? (
          <div className="text-center" style={{ color: "var(--text-muted)", padding: "40px" }}>
            Carregando lista de inscritos...
          </div>
        ) : registrations.length > 0 ? (
          <div className="table-responsive">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>E-mail</th>
                  <th>Inscrito em</th>
                </tr>
              </thead>
              <tbody>
                {registrations.map((reg, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: "600" }}>{reg.name}</td>
                    <td>{reg.email}</td>
                    <td className="text-muted" style={{ fontSize: "14px" }}>
                      {new Date(reg.registered_at).toLocaleString("pt-BR")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center" style={{ padding: "60px 0", border: "1px dashed var(--border)", borderRadius: "var(--radius-lg)", background: "var(--surface)" }}>
            <p className="text-muted" style={{ fontSize: "16px", marginBottom: "16px" }}>
              Nenhum participante inscrito neste evento ainda.
            </p>
            <Link to="/events/me/" className="btn btn-outline">
              Voltar ao Painel
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
