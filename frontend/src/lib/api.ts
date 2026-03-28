const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`);
  }
  return res.json() as Promise<T>;
}

export interface Gasto {
  id: number;
  monto: string;
  descripcion: string;
  categoria: string;
  subcategoria: string | null;
  fuente: string;
  referencia_externa: string | null;
  fecha: string;
  creado_en: string;
}

export function getGastos(): Promise<Gasto[]> {
  return fetchJson<Gasto[]>("/api/gastos/");
}
