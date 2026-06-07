<script>
  import { createEventDispatcher } from 'svelte';

  export let config;
  export let questions = [];

  const dispatch = createEventDispatcher();

  // Se mantiene un flujo visual de chat sin IA real conectada.
  const assistantNotes = [
    'Estoy simulando la respuesta del candidato para esta fase.',
    'Todavia no hay modelo conectado. Este texto es un placeholder funcional.',
    'Cuando conectemos FastAPI, esta tarjeta consumira respuestas reales.'
  ];

  let currentQuestionIndex = 0;
  let transcript = [
    {
      role: 'system',
      label: 'Simulacion activa',
      content: 'La IA real aun no esta conectada. Este chat funciona como previsualizacion del flujo.'
    }
  ];

  function currentQuestion() {
    return questions[currentQuestionIndex] ?? null;
  }

  function addInterviewPrompt() {
    const item = currentQuestion();

    if (!item) {
      return;
    }

    transcript = [
      ...transcript,
      {
        role: 'interviewer',
        label: `Pregunta ${currentQuestionIndex + 1}`,
        content: item.prompt
      }
    ];
  }

  function simulateCandidateReply() {
    const item = currentQuestion();

    if (!item) {
      return;
    }

    const note = assistantNotes[currentQuestionIndex % assistantNotes.length];

    transcript = [
      ...transcript,
      {
        role: 'candidate',
        label: 'Respuesta simulada',
        content: `${note} Mi enfoque para ${item.category.toLowerCase()} seria estructurar una respuesta clara, con contexto, decision y resultado.`
      }
    ];
  }

  function nextQuestion() {
    if (!questions.length) {
      return;
    }

    currentQuestionIndex = (currentQuestionIndex + 1) % questions.length;
    addInterviewPrompt();
  }

  function startCurrentQuestion() {
    addInterviewPrompt();
  }

  function backToQuestions() {
    dispatch('back');
  }

  function goToEvaluation() {
    dispatch('continue');
  }
</script>

<section class="chat-card">
  <header class="chat-header">
    <div>
      <p class="eyebrow">Paso 3</p>
      <h2>Chat con IA</h2>
      <p>
        Aqui ira la IA real mas por ahora la experiencia esta simulada para probar el flujo completo.
        El objetivo es validar la interfaz, el ritmo de la entrevista y la transicion entre fases.
      </p>
    </div>
    <div class="chat-meta" aria-label="Contexto de la simulacion">
      <span class="config-chip">{config.jobRole}</span>
      <span class="config-chip">{config.seniority}</span>
      <span class="config-chip">IA no conectada</span>
    </div>
  </header>

  <div class="chat-placeholder">
    <div class="placeholder-ribbon">Placeholder de IA</div>
    <p>
      Este bloque marcara el punto exacto donde se integrara el modelo. De momento los botones producen
      una experiencia guiada con respuestas simuladas.
    </p>
  </div>

  <div class="chat-layout">
    <aside class="chat-sidebar">
      <h3>Control de simulacion</h3>
      <p>Selecciona una pregunta y genera respuestas falsas para validar el recorrido.</p>

      <div class="chat-actions">
        <button type="button" class="btn-primary" on:click={startCurrentQuestion}>Lanzar pregunta</button>
        <button type="button" class="btn-secondary" on:click={simulateCandidateReply}>Simular respuesta</button>
        <button type="button" class="btn-secondary" on:click={nextQuestion}>Siguiente pregunta</button>
      </div>

      <div class="chat-summary">
        <span>Pregunta activa</span>
        <strong>{currentQuestionIndex + 1} / {questions.length || 0}</strong>
      </div>

      {#if currentQuestion()}
        <div class="chat-current-question">
          <p class="question-kicker">{currentQuestion().category}</p>
          <h4>{currentQuestion().title}</h4>
        </div>
      {/if}
    </aside>

    <div class="chat-board">
      <div class="chat-board-header">
        <strong>Conversacion simulada</strong>
        <span>Mensajes de ejemplo hasta conectar FastAPI</span>
      </div>

      <div class="chat-messages">
        {#each transcript as message}
          <article class={`chat-message ${message.role}`}>
            <span class="chat-label">{message.label}</span>
            <p>{message.content}</p>
          </article>
        {/each}
      </div>

      <div class="chat-footer">
        <p>
          Cuando la IA real entre, este panel pasara a mostrar turnos de usuario, respuestas del modelo y
          feedback inmediato.
        </p>
        <div class="cta-row">
          <button type="button" class="btn-secondary" on:click={backToQuestions}>Volver a preguntas</button>
          <button type="button" class="btn-primary" on:click={goToEvaluation}>Ir a evaluar respuestas</button>
        </div>
      </div>
    </div>
  </div>
</section>
