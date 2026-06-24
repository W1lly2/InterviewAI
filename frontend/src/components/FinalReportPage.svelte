<script>
  import { createEventDispatcher } from 'svelte';

  export let evaluation = null;
  export let questions = [];
  export let config;

  const dispatch = createEventDispatcher();

  const fallbackRecommendations = [
    'Practicar respuestas con estructura situacion -> accion -> resultado.',
    'Añadir ejemplos concretos con metricas o impacto en negocio.',
    'Reducir explicaciones largas y priorizar decisiones clave.'
  ];

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function keywordHits(text, keywords) {
    const lower = String(text || '').toLowerCase();
    return keywords.reduce((acc, k) => (lower.includes(k) ? acc + 1 : acc), 0);
  }

  $: feedbackItems = evaluation?.feedback_items ?? [];
  $: hasEvaluation = feedbackItems.length > 0;
  $: overallScore = hasEvaluation ? Number(evaluation.overall_score || 0) : 82;

  $: sortedByScore = [...feedbackItems].sort((a, b) => b.score - a.score);
  $: bestItem = sortedByScore[0] ?? null;
  $: worstItem = sortedByScore[sortedByScore.length - 1] ?? null;

  $: reportSummary = [
    { label: 'Score global', value: `${overallScore}/100` },
    {
      label: 'Fortaleza principal',
      value: bestItem ? `P${bestItem.question_number} (${bestItem.score}/100)` : 'Arquitectura y claridad'
    },
    {
      label: 'Area a reforzar',
      value: worstItem ? `P${worstItem.question_number} (${worstItem.score}/100)` : 'Profundidad en trade-offs'
    }
  ];

  $: recommendations = hasEvaluation
    ? Array.from(
        new Set(
          feedbackItems
            .map((item) => item.recommendation)
            .filter(Boolean)
        )
      ).slice(0, 6)
    : fallbackRecommendations;

  $: questionChart = hasEvaluation
    ? feedbackItems.map((item, index) => ({
        label: `P${item.question_number || index + 1}`,
        score: clamp(Number(item.score || 0), 0, 100),
        title: item.question || `Pregunta ${index + 1}`
      }))
    : questions.slice(0, 6).map((_, index) => ({
        label: `P${index + 1}`,
        score: 74 + (index % 3) * 5,
        title: `Pregunta ${index + 1}`
      }));

  $: avgScore = questionChart.length
    ? questionChart.reduce((acc, item) => acc + item.score, 0) / questionChart.length
    : overallScore;

  $: clarityScore = clamp(
    Math.round(
      avgScore * 0.75 +
        feedbackItems.reduce((acc, item) => acc + (item.strengths?.length || 0) * 4, 0) /
          Math.max(1, feedbackItems.length)
    ),
    40,
    100
  );

  $: depthScore = clamp(
    Math.round(
      avgScore * 0.7 +
        feedbackItems.reduce(
          (acc, item) =>
            acc +
            keywordHits(item.answer, ['trade-off', 'riesgo', 'decision', 'arquitectura', 'escala']) * 6,
          0
        ) /
          Math.max(1, feedbackItems.length)
    ),
    35,
    100
  );

  $: communicationScore = clamp(
    Math.round(
      avgScore * 0.8 +
        feedbackItems.reduce((acc, item) => acc + clamp((item.answer || '').split(' ').length / 6, 0, 12), 0) /
          Math.max(1, feedbackItems.length)
    ),
    40,
    100
  );

  $: impactScore = clamp(
    Math.round(
      avgScore * 0.68 +
        feedbackItems.reduce(
          (acc, item) => acc + keywordHits(item.answer, ['resultado', 'impacto', 'metrica', 'kpi', 'p95']) * 8,
          0
        ) /
          Math.max(1, feedbackItems.length)
    ),
    30,
    100
  );

  $: competencyChart = [
    { label: 'Claridad', score: clarityScore },
    { label: 'Profundidad', score: depthScore },
    { label: 'Comunicacion', score: communicationScore },
    { label: 'Impacto', score: impactScore }
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
        Resumen consolidado de desempeno para {config?.jobRole || 'el rol objetivo'} ({config?.seniority || 'nivel'}) con foco en fortalezas, brechas y plan de mejora.
      </p>
    </div>
    <div class="config-chip-wrap" aria-label="Resumen final">
      <span class="config-chip">{hasEvaluation ? 'Evaluacion activa' : 'Modo fallback'}</span>
      <span class="config-chip">{questionChart.length} respuestas analizadas</span>
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
      <p class="summary-note">{evaluation?.summary || 'Se muestra una lectura preliminar basada en el comportamiento observado.'}</p>
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

  <div class="chart-grid">
    <article class="report-panel">
      <h3>Grafica por pregunta</h3>
      <div class="bar-chart" aria-label="Desempeno por pregunta">
        {#each questionChart as item}
          <div class="bar-row" title={item.title}>
            <span class="bar-label">{item.label}</span>
            <div class="bar-track">
              <div class="bar-fill" style={`width: ${item.score}%`}>
                <span class="bar-score">{item.score}</span>
              </div>
            </div>
          </div>
        {/each}
      </div>
    </article>

    <article class="report-panel">
      <h3>Desglose por competencia</h3>
      <div class="competency-grid">
        {#each competencyChart as metric}
          <div class="competency-card">
            <span>{metric.label}</span>
            <strong>{metric.score}</strong>
            <div class="mini-track">
              <div class="mini-fill" style={`height: ${metric.score}%`}></div>
            </div>
          </div>
        {/each}
      </div>
    </article>
  </div>

  <article class="report-panel improvements-panel">
    <h3>Historial de mejoras sugeridas</h3>
    <div class="improvement-list">
      {#if hasEvaluation}
        {#each feedbackItems as item}
          <div class="improvement-item">
            <div class="improvement-head">
              <strong>P{item.question_number}</strong>
              <span>{item.score}/100</span>
            </div>
            <p>{item.recommendation}</p>
          </div>
        {/each}
      {:else}
        <div class="improvement-item">
          <div class="improvement-head">
            <strong>Referencia</strong>
            <span>Preliminar</span>
          </div>
          <p>Completa una evaluacion para habilitar recomendaciones por respuesta.</p>
        </div>
      {/if}
    </div>
  </article>

  <div class="cta-row">
    <button type="button" class="btn-secondary" on:click={backToEvaluation}>Volver a evaluar</button>
    <button type="button" class="btn-primary" on:click={startNewInterview}>Nueva entrevista</button>
  </div>
</section>

<style>
  .report-card {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    padding: 1.75rem;
    background: #f6f8f7;
    border: 1px solid #c7d7d2;
    border-radius: 16px;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }

  .eyebrow {
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.8rem;
    font-weight: 700;
    color: #35554b;
  }

  h2,
  h3 {
    margin: 0.35rem 0 0.7rem;
    color: #0f2f2a;
  }

  .section-header p,
  .summary-note {
    margin: 0;
    color: #35554b;
    line-height: 1.45;
  }

  .config-chip-wrap {
    display: flex;
    gap: 0.65rem;
    flex-wrap: wrap;
    align-content: flex-start;
  }

  .config-chip {
    border-radius: 999px;
    border: 1px solid #a7c1b8;
    color: #0f4a42;
    background: #eaf3ef;
    font-weight: 700;
    font-size: 0.85rem;
    padding: 0.5rem 0.85rem;
  }

  .report-grid,
  .chart-grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: 1fr 1fr;
  }

  .report-panel {
    background: #ffffff;
    border: 1px solid #c7d7d2;
    border-radius: 14px;
    padding: 1rem;
  }

  .report-metrics {
    display: grid;
    gap: 0.65rem;
  }

  .report-metric {
    border: 1px solid #c7d7d2;
    border-radius: 10px;
    padding: 0.7rem 0.85rem;
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    color: #35554b;
  }

  .report-metric strong {
    color: #0f2f2a;
  }

  .recommendation-list {
    margin: 0;
    padding-left: 1.2rem;
    display: grid;
    gap: 0.55rem;
    color: #163934;
  }

  .bar-chart {
    display: grid;
    gap: 0.65rem;
  }

  .bar-row {
    display: grid;
    grid-template-columns: 2.8rem 1fr;
    gap: 0.5rem;
    align-items: center;
  }

  .bar-label {
    font-weight: 700;
    color: #35554b;
    font-size: 0.82rem;
  }

  .bar-track {
    position: relative;
    height: 1.25rem;
    border-radius: 999px;
    background: #e5efeb;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    min-width: 2rem;
    border-radius: 999px;
    background: linear-gradient(90deg, #176b63, #2a8b7d);
  }

  .bar-score {
    color: #f6fffc;
    font-size: 0.75rem;
    font-weight: 700;
    margin-right: 0.45rem;
  }

  .competency-grid {
    display: grid;
    gap: 0.8rem;
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .competency-card {
    display: grid;
    justify-items: center;
    gap: 0.35rem;
    background: #f4fbf8;
    border: 1px solid #d1e4dd;
    border-radius: 10px;
    padding: 0.6rem 0.45rem;
  }

  .competency-card span {
    font-size: 0.78rem;
    color: #35554b;
  }

  .competency-card strong {
    font-size: 1.1rem;
    color: #0f2f2a;
  }

  .mini-track {
    height: 76px;
    width: 20px;
    border-radius: 999px;
    background: #dcebe5;
    display: flex;
    align-items: flex-end;
    overflow: hidden;
  }

  .mini-fill {
    width: 100%;
    background: linear-gradient(0deg, #14574f, #3ea08f);
  }

  .improvements-panel {
    display: grid;
    gap: 0.8rem;
  }

  .improvement-list {
    display: grid;
    gap: 0.65rem;
  }

  .improvement-item {
    border: 1px solid #cfe0da;
    border-radius: 10px;
    padding: 0.7rem 0.85rem;
    background: #fcfefe;
  }

  .improvement-head {
    display: flex;
    justify-content: space-between;
    color: #35554b;
    margin-bottom: 0.35rem;
  }

  .improvement-item p {
    margin: 0;
    color: #163934;
  }

  .cta-row {
    display: flex;
    justify-content: flex-end;
    gap: 0.8rem;
  }

  .btn-primary,
  .btn-secondary {
    border: none;
    border-radius: 999px;
    padding: 0.7rem 1.1rem;
    font-weight: 700;
    cursor: pointer;
  }

  .btn-secondary {
    background: #dde9e4;
    color: #18423c;
  }

  .btn-primary {
    background: #0e6f64;
    color: #f1fffb;
  }

  @media (max-width: 960px) {
    .section-header {
      flex-direction: column;
    }

    .report-grid,
    .chart-grid {
      grid-template-columns: 1fr;
    }

    .competency-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .cta-row {
      flex-direction: column;
      align-items: stretch;
    }
  }
</style>
