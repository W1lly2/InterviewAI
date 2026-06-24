<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { fetchAiStatus } from '../modules/api/ai.ts';
  import {
    loadInterviewTranscript,
    startSession,
    submitAnswerTurn
  } from '../modules/interviewSession/chatService.ts';
  import { interviewSessionStore } from '../modules/interviewSession/sessionStore.ts';
  import { mapSessionMessagesToUi } from '../modules/interviewSession/transcriptMapper.ts';

  export let config;
  export let questions = [];

  const dispatch = createEventDispatcher();

  // Estado de conexion con Ollama.
  let aiReachable = false;
  let aiModel = '';
  let statusChecked = false;

  // Texto que escribe el usuario candidato.
  let userInput = '';

  // Indica si hay una respuesta de IA en curso.
  let waiting = false;

  // Error visible para el usuario.
  let errorMessage = '';

  // Estado local sincronizado desde session store.
  let interviewId = null;
  let currentQuestionIndex = 0;
  let totalQuestions = questions.length;
  let followUpStage = 0;
  let interviewComplete = false;
  let lastTurnSource = '';
  let lastLatencyMs = 0;
  let transcript = [];

  const unsubscribe = interviewSessionStore.subscribe((state) => {
    interviewId = state.interviewId;
    currentQuestionIndex = state.currentQuestionIndex;
    totalQuestions = state.totalQuestions;
    followUpStage = state.followUpStage;
    interviewComplete = state.interviewComplete;
    lastTurnSource = state.turnSource;
    lastLatencyMs = state.lastLatencyMs;
    transcript = mapSessionMessagesToUi(state.messages);
  });

  // Envia la respuesta del candidato y obtiene reaccion del entrevistador IA.
  async function submitAnswer() {
    const text = userInput.trim();

    if (!text || waiting || !interviewId || !aiReachable) return;

    interviewSessionStore.pushCandidateAnswer(text);
    userInput = '';
    waiting = true;
    errorMessage = '';

    try {
      const turn = await submitAnswerTurn(interviewId, text);
      interviewSessionStore.pushInterviewerTurn({
        reply: turn.reply,
        source: turn.source,
        currentQuestionIndex: turn.current_question_index,
        totalQuestions: turn.total_questions,
        followUpStage: turn.follow_up_stage,
        interviewComplete: turn.interview_complete,
        latencyMs: turn.latency_ms,
        turnType: turn.turn_type
      });
    } catch (err) {
      errorMessage = err.message ?? 'Error al conectar con el backend.';
    } finally {
      waiting = false;
    }
  }

  // Permite enviar con Enter (sin Shift).
  function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      submitAnswer();
    }
  }

  // Verifica disponibilidad de Ollama al montar el componente.
  onMount(() => {
    interviewSessionStore.reset();

    void (async () => {
      try {
        const status = await fetchAiStatus();
        aiReachable = status.reachable;
        aiModel = status.configured_model;
      } catch {
        aiReachable = false;
      } finally {
        statusChecked = true;

        if (aiReachable && questions.length) {
          try {
            const started = await startSession(config, questions);
            interviewSessionStore.setStarted({
              interviewId: started.interview_id,
              reply: started.reply,
              source: started.source,
              currentQuestionIndex: started.current_question_index,
              totalQuestions: started.total_questions,
              followUpStage: started.follow_up_stage,
              interviewComplete: started.interview_complete,
              latencyMs: started.latency_ms
            });
          } catch (err) {
            errorMessage = err.message ?? 'No se pudo iniciar la sesion de entrevista.';
          }
        }
      }
    })();

    return () => {
      unsubscribe();
    };
  });

  async function continueToEvaluation() {
    if (!interviewId) return;

    try {
      const canonicalTranscript = await loadInterviewTranscript(interviewId);
      dispatch('continue', {
        interviewId,
        transcript: canonicalTranscript
      });
    } catch {
      dispatch('continue', {
        interviewId,
        transcript
      });
    }
  }
</script>

<section class="chat-card">
  <header class="chat-header">
    <div>
      <p class="eyebrow">Paso 3</p>
      <h2>Chat con IA</h2>
      <p>
        Responde las preguntas del entrevistador. La IA adaptara el siguiente turno
        segun tu respuesta.
      </p>
    </div>

    <div class="chat-meta" aria-label="Contexto de la sesion">
      <span class="config-chip">{config.jobRole}</span>
      <span class="config-chip">{config.seniority}</span>
      <span class="config-chip">Q {currentQuestionIndex + 1}/{totalQuestions || 0}</span>
      {#if statusChecked}
        <span class="config-chip {aiReachable ? '' : 'chip-error'}">
          {aiReachable ? aiModel : 'IA sin conexion'}
        </span>
      {/if}
      {#if lastTurnSource}
        <span class="config-chip {lastTurnSource === 'fallback' ? 'chip-error' : ''}">
          Turno: {lastTurnSource}
        </span>
      {/if}
    </div>
  </header>

  {#if statusChecked && !aiReachable}
    <div class="chat-placeholder">
      <div class="placeholder-ribbon">Ollama no responde</div>
      <p>
        Asegurate de tener Ollama activo y el modelo descargado:
        <code>ollama pull {aiModel || 'llama3.2:1b'}</code>
      </p>
    </div>
  {/if}

  <div class="chat-layout">
    <aside class="chat-sidebar">
      <h3>Preguntas preparadas</h3>
      <p>El backend controla el stage y el avance automaticamente.</p>

      <div class="chat-summary">
        <span>Pregunta activa</span>
        <strong>{currentQuestionIndex + 1} / {totalQuestions || questions.length || 0}</strong>
      </div>

      <div class="chat-summary">
        <span>Profundizacion</span>
        <strong>{followUpStage}</strong>
      </div>

      {#if lastLatencyMs > 0}
        <div class="chat-summary">
          <span>Latencia ultimo turno</span>
          <strong>{lastLatencyMs} ms</strong>
        </div>
      {/if}

      {#if questions[currentQuestionIndex]}
        <div class="chat-current-question">
          <p class="question-kicker">{questions[currentQuestionIndex].category}</p>
          <h4>{questions[currentQuestionIndex].title}</h4>
        </div>
      {/if}
    </aside>

    <div class="chat-board">
      <div class="chat-board-header">
        <strong>Entrevista en curso</strong>
        <span>
          {interviewComplete
            ? 'Entrevista completada'
            : aiReachable
              ? `Modelo: ${aiModel}`
              : 'Backend no disponible'}
        </span>
      </div>

      <div class="chat-messages">
        {#each transcript as message (message)}
          <article class={`chat-message ${message.role}`}>
            <span class="chat-label">
              {message.label}
              {#if message.role === 'interviewer'}
                {' '}· {message.source}
              {/if}
            </span>
            <p>{message.content}</p>
          </article>
        {/each}

        {#if waiting}
          <article class="chat-message interviewer">
            <span class="chat-label">Entrevistador</span>
            <p class="thinking">Pensando...</p>
          </article>
        {/if}
      </div>

      {#if errorMessage}
        <p class="chat-error">{errorMessage}</p>
      {/if}

      <div class="chat-input-row">
        <textarea
          bind:value={userInput}
          on:keydown={handleKeydown}
          rows="3"
          placeholder="Escribe tu respuesta y presiona Enter para enviar..."
          disabled={waiting || !aiReachable || interviewComplete}
        ></textarea>
        <button
          type="button"
          class="btn-primary"
          disabled={waiting || !userInput.trim() || !aiReachable || interviewComplete}
          on:click={submitAnswer}
        >
          {waiting ? 'Enviando...' : 'Enviar'}
        </button>
      </div>

      <div class="cta-row">
        <button type="button" class="btn-secondary" on:click={() => dispatch('back')}>
          Volver a preguntas
        </button>
        <button 
          type="button" 
          class="btn-primary" 
          disabled={!interviewId}
          on:click={continueToEvaluation}
        >
          Ir a evaluar respuestas
        </button>
      </div>
    </div>
  </div>
</section>
