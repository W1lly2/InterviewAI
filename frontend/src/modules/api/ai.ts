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

export interface FeedbackItem {
  question_number: number;
  question: string;
  answer: string;
  strengths: string[];
  gaps: string[];
  recommendation: string;
  score: number;
}

export interface EvaluationResponse {
  feedback_items: FeedbackItem[];
  overall_score: number;
  summary: string;
}

export interface InterviewConfig {
  jobRole: string;
  seniority: string;
  interviewType: string;
  stack?: string;
}

export interface InterviewQuestion {
  category: string;
  title: string;
  prompt: string;
}

export interface InterviewTurn {
  interview_id: string;
  turn_type: string;
  source: string;
  reply: string;
  current_question_index: number;
  total_questions: number;
  follow_up_stage: number;
  interview_complete: boolean;
  tags: string[];
  latency_ms: number;
}

type ApiErrorBody = {
  detail?: string | Array<{ msg?: string; loc?: Array<string | number> }> | Record<string, unknown>;
};

function parseApiErrorDetail(detail: ApiErrorBody['detail'], status: number): string {
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length) {
    const first = detail[0];
    const where = first?.loc?.length ? ` (${first.loc.join('.')})` : '';
    const message = first?.msg ?? 'Solicitud invalida.';
    return `${message}${where}`;
  }

  if (detail && typeof detail === 'object') {
    return `Error ${status}: ${JSON.stringify(detail)}`;
  }

  return `Error ${status}`;
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as ApiErrorBody;
    throw new Error(parseApiErrorDetail(body.detail, res.status));
  }

  return res.json() as Promise<T>;
}

// --- Funciones ---

/**
 * Comprueba si el backend con Ollama esta disponible.
 */
export async function fetchAiStatus(): Promise<AiStatus> {
  return requestJson<AiStatus>(`${API_BASE}/ai/status`);
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
  return requestJson<ChatResponse>(`${API_BASE}/ai/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, system_prompt: systemPrompt })
  });
}

/**
 * Envia el transcript del chat para evaluacion con IA.
 * @param transcript - Array de mensajes {role, content}
 * @param context - Contexto opcional (puesto, seniority, tipo)
 */
export async function requestEvaluation(
  transcript: Array<{ role: string; content: string }>,
  context?: string
): Promise<EvaluationResponse> {
  return requestJson<EvaluationResponse>(`${API_BASE}/ai/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      transcript,
      interview_context: context
    })
  });
}

/**
 * Crea una sesion de entrevista y devuelve la primera intervencion del entrevistador.
 */
export async function startInterviewSession(
  config: InterviewConfig,
  questions: InterviewQuestion[]
): Promise<InterviewTurn> {
  return requestJson<InterviewTurn>(`${API_BASE}/interviews/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ config, questions })
  });
}

/**
 * Envia respuesta del candidato para obtener siguiente turno del entrevistador.
 */
export async function submitInterviewTurn(
  interviewId: string,
  answer: string
): Promise<InterviewTurn> {
  return requestJson<InterviewTurn>(`${API_BASE}/interviews/${interviewId}/turn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answer })
  });
}

/**
 * Ejecuta evaluacion final de sesion estructurada.
 */
export async function evaluateInterviewSession(interviewId: string): Promise<EvaluationResponse> {
  return requestJson<EvaluationResponse>(`${API_BASE}/interviews/${interviewId}/evaluate`, {
    method: 'POST'
  });
}

/**
 * Obtiene transcript canonico desde backend.
 */
export async function fetchInterviewTranscript(
  interviewId: string
): Promise<Array<{ role: string; source?: string; content: string }>> {
  return requestJson<Array<{ role: string; source?: string; content: string }>>(
    `${API_BASE}/interviews/${interviewId}/transcript`
  );
}

