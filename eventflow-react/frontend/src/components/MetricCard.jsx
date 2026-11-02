export default function MetricCard({ title, value, icon }) {
  return (
    <div className="metric-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span className="metric-title">{title}</span>
        {icon && <span style={{ fontSize: "20px" }}>{icon}</span>}
      </div>
      <span className="metric-value">{value}</span>
    </div>
  );
}
