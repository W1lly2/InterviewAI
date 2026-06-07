<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { fetchAiStatus, sendChatMessage } from '../modules/api/ai.ts';

  export let config;
  export let questions = [];

  const dispatch = createEventDispatcher();

  // Estado de conexion con Ollama.
  let aiReachable = false;
  let aiModel = '';
  let statusChecked = false;

  // Indice de la pregunta activa.
  let currentQuestionIndex = 0;

  // Texto que escribe el usuario candidato.
  let userInput = '';

  // Indica si hay una respuesta de IA en curso.
  let waiting = false;

  // Error visible para el usuario.
  let errorMessage = '';

  // Historial de turnos de la entrevista.
  let transcript = [];

  // Construye el prompt de sistema para el entrevistador segun la configuracion.
  function buildSystemPrompt() {
    return [
      `Eres un entrevistador tecnico experto para el puesto de ${config.jobRole}, nivel ${config.seniority}.`,
      `El tipo de entrevista es: ${config.interviewType}.`,
      `El stack del candidato incluye: ${config.stack || 'general'}.`,
      'Tu rol es hacer preguntas claras, profundas y adaptar el nivel segun las respuestas.',
      'Si la respuesta es vaga, repregunta pidiendo ejemplos concretos o metricas.',
      'Responde siempre en espanol. Sé directo y profesional.'
    ].join('\n');
  }

  // Lanza la pregunta activa al transcript como turno de entrevistador.
  function launchCurrentQuestion() {
    const item = questions[currentQuestionIndex];

    if (!item) return;

    transcript = [
      ...transcript,
      {
        role: 'interviewer',
        label: `Pregunta ${currentQuestionIndex + 1} · ${item.category}`,
        content: item.prompt
      }
    ];
  }

  // Avanza a la siguiente pregunta.
  function nextQuestion() {
    if (!questions.length) return;

    currentQuestionIndex = Math.min(currentQuestionIndex + 1, questions.length - 1);
    launchCurrentQuestion();
  }

  // Envia la respuesta del candidato y obtiene reaccion del entrevistador IA.
  async function submitAnswer() {
    const text = userInput.trim();

    if (!text || waiting) return;

    // Agrega turno candidato al transcript.
    transcript = [
      ...transcript,
      { role: 'candidate', label: 'Tu respuesta', content: text }
    ];
    userInput = '';
    waiting = true;
    errorMessage = '';

    try {
      // Construye contexto completo como prompt para Ollama.
      const contextHistory = transcript
        .map((t) => `[${t.label}]: ${t.content}`)
        .join('\n\n');

      const data = await sendChatMessage(contextHistory, buildSystemPrompt());

      transcript = [
        ...transcript,
        {
          role: 'interviewer',
          label: `Entrevistador (${data.model})`,
          content: data.reply
        }
      ];
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
  onMount(async () => {
    try {
      const status = await fetchAiStatus();
      aiReachable = status.reachable;
      aiModel = status.configured_model;
    } catch {
      aiReachable = false;
    } finally {
      statusChecked = true;

      // Lanza la primera pregunta automaticamente si hay conexion.
      if (aiReachable && questions.length) {
        launchCurrentQuestion();
      }
    }
  });
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
      {#if statusChecked}
        <span class="config-chip {aiReachable ? '' : 'chip-error'}">
          {aiReachable ? aiModel : 'IA sin conexion'}
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
      <p>Avanza manualmente si quieres saltar a la siguiente.</p>

      <div class="chat-actions">
        <button
          type="button"
          class="btn-secondary"
          disabled={waiting || currentQuestionIndex >= questions.length - 1}
          on:click={nextQuestion}
        >
          Siguiente pregunta
        </button>
      </div>

      <div class="chat-summary">
        <span>Pregunta activa</span>
        <strong>{currentQuestionIndex + 1} / {questions.length || 0}</strong>
      </div>

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
        <span>{aiReachable ? `Modelo: ${aiModel}` : 'Backend no disponible'}</span>
      </div>

      <div class="chat-messages">
        {#each transcript as message (message)}
          <article class={`chat-message ${message.role}`}>
            <span class="chat-label">{message.label}</span>
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
          disabled={waiting || !aiReachable}
        ></textarea>
        <button
          type="button"
          class="btn-primary"
          disabled={waiting || !userInput.trim() || !aiReachable}
          on:click={submitAnswer}
        >
          {waiting ? 'Enviando...' : 'Enviar'}
        </button>
      </div>

      <div class="cta-row">
        <button type="button" class="btn-secondary" on:click={() => dispatch('back')}>
          Volver a preguntas
        </button>
        <button type="button" class="btn-primary" on:click={() => dispatch('continue')}>
          Ir a evaluar respuestas
        </button>
      </div>
    </div>
  </div>
</section>
