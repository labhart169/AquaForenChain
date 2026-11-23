export default function EvidenceTable({rows=[]}) {
  return <table><thead><tr><th>Evidence</th><th>Event</th><th>Device</th><th>Type</th><th>Severity</th></tr></thead><tbody>{rows.slice(0,20).map((r,i)=><tr key={i}><td>{r.evidence_id}</td><td>{r.event_id}</td><td>{r.device_id}</td><td>{r.event_type}</td><td>{r.severity}</td></tr>)}</tbody></table>;
}
