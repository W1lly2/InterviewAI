import type { SessionMessage } from './sessionStore';

export type UiTranscriptItem = {
  role: 'interviewer' | 'candidate';
  label: string;
  content: string;
  source: 'ai' | 'system' | 'fallback' | 'user';
};

export function mapSessionMessagesToUi(messages: SessionMessage[]): UiTranscriptItem[] {
  return messages.map((message) => ({
    role: message.role,
    label: message.label,
    content: message.content,
    source: message.source
  }));
}

export function mapBackendTranscriptToUi(
  transcript: Array<{ role: string; source?: string; content: string }>
): UiTranscriptItem[] {
  return transcript
    .filter((item) => item.role === 'interviewer' || item.role === 'candidate')
    .map((item, index) => ({
      role: item.role as 'interviewer' | 'candidate',
      label: item.role === 'interviewer' ? `Entrevistador ${index + 1}` : 'Tu respuesta',
      content: item.content,
      source: (item.source as 'ai' | 'system' | 'fallback' | 'user') || 'system'
    }));
}
