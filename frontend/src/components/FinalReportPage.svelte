<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  // Resumen base para el reporte final mientras no exista evaluacion real.
  const reportSummary = [
    { label: 'Score global', value: '82/100' },
    { label: 'Fortalezas', value: 'Arquitectura y claridad' },
    { label: 'Area a mejorar', value: 'Profundidad en trade-offs' }
  ];

  const recommendations = [
    'Practicar respuestas con estructura situacion -> accion -> resultado.',
    'Añadir ejemplos concretos con metricas o impacto en negocio.',
    'Reducir explicaciones largas y priorizar decisiones clave.'
  ];

  function backToEvaluation() {
    dispatch('back');
  }

  function startNewInterview() {
    dispatch('restart');
  }
</script>

<section class="report-card">
  <header class="section-header">
    <div>
      <p class="eyebrow">Paso 5</p>
      <h2>Reporte final</h2>
      <p>
        Este resumen es un placeholder de entrega para visualizar como se presentara el resultado
        final cuando la evaluacion automatica este conectada.
      </p>
    </div>
    <div class="config-chip-wrap" aria-label="Resumen final">
      <span class="config-chip">Simulacion activa</span>
      <span class="config-chip">Reporte preliminar</span>
    </div>
  </header>

  <div class="report-grid">
    <article class="report-panel report-summary-panel">
      <h3>Resumen ejecutivo</h3>
      <div class="report-metrics">
        {#each reportSummary as item}
          <div class="report-metric">
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </div>
        {/each}
      </div>
    </article>

    <article class="report-panel">
      <h3>Recomendaciones</h3>
      <ul class="recommendation-list">
        {#each recommendations as recommendation}
          <li>{recommendation}</li>
        {/each}
      </ul>
    </article>
  </div>

  <div class="phase-placeholder">
    <p>
      Placeholder final: aqui iran graficas, desglose por competencia y un historial de respuestas con
      mejora sugerida.
    </p>
    <div class="cta-row">
      <button type="button" class="btn-secondary" on:click={backToEvaluation}>Volver a evaluar</button>
      <button type="button" class="btn-primary" on:click={startNewInterview}>Nueva entrevista</button>
    </div>
  </div>
</section>
