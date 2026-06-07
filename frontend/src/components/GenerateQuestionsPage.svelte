<script>
  import { createEventDispatcher } from 'svelte';

  export let config;
  export let questions = [];

  const dispatch = createEventDispatcher();

  function regenerate() {
    dispatch('regenerate');
  }

  function continueToChat() {
    dispatch('continue');
  }
</script>

<section class="question-card">
  <header class="question-header">
    <div>
      <p class="eyebrow">Paso 2</p>
      <h2>Generar preguntas</h2>
      <p>
        Estas preguntas estan preparadas para un perfil <strong>{config.seniority}</strong> de
        <strong>{config.jobRole}</strong> con enfoque <strong>{config.interviewType}</strong>.
      </p>
    </div>
    <div class="config-chip-wrap" aria-label="Resumen de configuracion">
      <span class="config-chip">{config.duration} min</span>
      <span class="config-chip">{config.stack || 'Stack general'}</span>
    </div>
  </header>

  <div class="question-grid">
    {#each questions as question, index}
      <article class="question-item">
        <p class="question-kicker">Pregunta {index + 1}</p>
        <h3>{question.title}</h3>
        <p>{question.prompt}</p>
        <span class="question-tag">{question.category}</span>
      </article>
    {/each}
  </div>

  <div class="cta-row questions-cta">
    <button type="button" class="btn-secondary" on:click={regenerate}>Regenerar set</button>
    <button type="button" class="btn-primary" on:click={continueToChat}>Iniciar chat con IA</button>
  </div>
</section>
