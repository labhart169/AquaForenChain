export const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
export async function getJSON(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
