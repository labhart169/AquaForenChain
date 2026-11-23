export default function SensorCard({name, value, unit}) {
  return <div className="card"><strong>{name}</strong><p>{value} {unit}</p></div>;
}
