import {
  evaluateInterviewSession,
  fetchInterviewTranscript,
  startInterviewSession,
  submitInterviewTurn,
  type EvaluationResponse,
  type InterviewConfig,
  type InterviewQuestion,
  type InterviewTurn
} from '../api/ai';

export async function startSession(
  config: InterviewConfig,
  questions: InterviewQuestion[]
): Promise<InterviewTurn> {
  return startInterviewSession(config, questions);
}

export async function submitAnswerTurn(
  interviewId: string,
  answer: string
): Promise<InterviewTurn> {
  return submitInterviewTurn(interviewId, answer);
}

export async function runInterviewEvaluation(interviewId: string): Promise<EvaluationResponse> {
  return evaluateInterviewSession(interviewId);
}

export async function loadInterviewTranscript(interviewId: string) {
  return fetchInterviewTranscript(interviewId);
}
