export default function MetricCard({title, value}) {
  return <div className="card"><div className="muted">{title}</div><div className="metric">{value}</div></div>;
}
