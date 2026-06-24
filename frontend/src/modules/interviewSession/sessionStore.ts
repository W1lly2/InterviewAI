import { writable } from 'svelte/store';

export type SessionMessage = {
  role: 'interviewer' | 'candidate';
  label: string;
  content: string;
  source: 'ai' | 'system' | 'fallback' | 'user';
};

export type InterviewSessionState = {
  interviewId: string | null;
  currentQuestionIndex: number;
  totalQuestions: number;
  followUpStage: number;
  interviewComplete: boolean;
  turnSource: 'ai' | 'system' | 'fallback' | 'user' | '';
  lastLatencyMs: number;
  messages: SessionMessage[];
};

const initialState: InterviewSessionState = {
  interviewId: null,
  currentQuestionIndex: 0,
  totalQuestions: 0,
  followUpStage: 0,
  interviewComplete: false,
  turnSource: '',
  lastLatencyMs: 0,
  messages: []
};

const { subscribe, set, update } = writable<InterviewSessionState>(initialState);

export const interviewSessionStore = {
  subscribe,
  reset: () => set(initialState),
  setStarted: (payload: {
    interviewId: string;
    reply: string;
    source: 'ai' | 'system' | 'fallback' | 'user';
    currentQuestionIndex: number;
    totalQuestions: number;
    followUpStage: number;
    interviewComplete: boolean;
    latencyMs: number;
  }) => {
    set({
      interviewId: payload.interviewId,
      currentQuestionIndex: payload.currentQuestionIndex,
      totalQuestions: payload.totalQuestions,
      followUpStage: payload.followUpStage,
      interviewComplete: payload.interviewComplete,
      turnSource: payload.source,
      lastLatencyMs: payload.latencyMs,
      messages: [
        {
          role: 'interviewer',
          label: payload.currentQuestionIndex >= 0
            ? `Pregunta ${payload.currentQuestionIndex + 1}`
            : 'Entrevistador',
          content: payload.reply,
          source: payload.source
        }
      ]
    });
  },
  pushCandidateAnswer: (answer: string) => {
    update((state) => ({
      ...state,
      messages: [
        ...state.messages,
        {
          role: 'candidate',
          label: 'Tu respuesta',
          content: answer,
          source: 'user'
        }
      ]
    }));
  },
  pushInterviewerTurn: (payload: {
    reply: string;
    source: 'ai' | 'system' | 'fallback' | 'user';
    currentQuestionIndex: number;
    totalQuestions: number;
    followUpStage: number;
    interviewComplete: boolean;
    latencyMs: number;
    turnType: string;
  }) => {
    update((state) => {
      const label = payload.turnType === 'follow_up'
        ? `Profundizacion ${payload.followUpStage}`
        : `Pregunta ${payload.currentQuestionIndex + 1}`;

      return {
        ...state,
        currentQuestionIndex: payload.currentQuestionIndex,
        totalQuestions: payload.totalQuestions,
        followUpStage: payload.followUpStage,
        interviewComplete: payload.interviewComplete,
        turnSource: payload.source,
        lastLatencyMs: payload.latencyMs,
        messages: [
          ...state.messages,
          {
            role: 'interviewer',
            label,
            content: payload.reply,
            source: payload.source
          }
        ]
      };
    });
  }
};
