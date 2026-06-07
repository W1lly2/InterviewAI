/**
 * Cliente HTTP del frontend para hablar con el backend FastAPI.
 * Usa la ruta /api para pasar por el proxy de Vite en desarrollo.
 */

const API_BASE = '/api/v1';

// --- Tipos ---

export interface AiStatus {
  configured_model: string;
  ollama_base_url: string;
  reachable: boolean;
}

export interface ChatResponse {
  model: string;
  reply: string;
}

// --- Funciones ---

/**
 * Comprueba si el backend con Ollama esta disponible.
 */
export async function fetchAiStatus(): Promise<AiStatus> {
  const res = await fetch(`${API_BASE}/ai/status`);

  if (!res.ok) {
    throw new Error(`Error al consultar estado: ${res.status}`);
  }

  return res.json() as Promise<AiStatus>;
}

/**
 * Envia un mensaje al entrevistador IA y obtiene la respuesta.
 * @param message - Texto del candidato o historial del chat.
 * @param systemPrompt - Instrucciones de contexto para la IA.
 */
export async function sendChatMessage(
  message: string,
  systemPrompt: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/ai/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, system_prompt: systemPrompt })
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(detail?.detail ?? `Error ${res.status}`);
  }

  return res.json() as Promise<ChatResponse>;
}
