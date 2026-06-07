<script>
  import { createEventDispatcher } from 'svelte';

  export let questions = [];

  const dispatch = createEventDispatcher();

  // Rubrica visual simple para simular la evaluacion sin backend.
  const criteria = [
    { name: 'Claridad', score: 4, note: 'Respuesta estructurada y facil de seguir.' },
    { name: 'Profundidad', score: 3, note: 'Buen nivel, pero falta mas detalle tecnico.' },
    { name: 'Impacto', score: 4, note: 'La respuesta conecta con resultados medibles.' },
    { name: 'Comunicacion', score: 5, note: 'Lenguaje claro, directo y adaptado al contexto.' }
  ];

  function backToChat() {
    dispatch('back');
  }

  function openFinalReport() {
    dispatch('continue');
  }
</script>

<section class="evaluation-card">
  <header class="section-header">
    <div>
      <p class="eyebrow">Paso 4</p>
      <h2>Evaluar respuestas</h2>
      <p>
        Esta pantalla todavia no usa IA real. Su objetivo es simular la lectura de respuestas, el
        scoring por criterio y el feedback que luego entregara el motor de evaluacion.
      </p>
    </div>
    <div class="config-chip-wrap" aria-label="Estado de la evaluacion">
      <span class="config-chip">{questions.length} preguntas</span>
      <span class="config-chip">Evaluacion simulada</span>
    </div>
  </header>

  <div class="evaluation-grid">
    <article class="evaluation-panel">
      <h3>Rubrica activa</h3>
      <p>Estas tarjetas son placeholders para el scoring real por competencia.</p>

      <div class="criterion-list">
        {#each criteria as criterion}
          <div class="criterion-item">
            <div>
              <strong>{criterion.name}</strong>
              <p>{criterion.note}</p>
            </div>
            <span class="criterion-score">{criterion.score}/5</span>
          </div>
        {/each}
      </div>
    </article>

    <article class="evaluation-panel">
      <h3>Feedback simulado</h3>
      <p>
        Aqui se mostrara el analisis automatico cuando FastAPI reciba el transcript del chat y lo
        procese con la IA real.
      </p>

      <div class="phase-placeholder">
        <p>
          Placeholder activo: detectamos fortalezas, brechas y una recomendacion puntual por pregunta.
        </p>
      </div>

      <div class="evaluation-actions">
        <button type="button" class="btn-secondary" on:click={backToChat}>Volver al chat</button>
        <button type="button" class="btn-primary" on:click={openFinalReport}>Ver reporte final</button>
      </div>
    </article>
  </div>
</section>
