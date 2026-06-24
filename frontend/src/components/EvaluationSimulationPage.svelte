<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { evaluateInterviewSession, requestEvaluation } from '../modules/api/ai.ts';

  export let config;
  export let questions = [];
  export let interviewId = null;
  export let transcript = [];

  const dispatch = createEventDispatcher();

  let evaluation = null;
  let loading = false;
  let errorMessage = '';

  // Solicita evaluacion al backend cuando monta.
  onMount(async () => {
    loading = true;
    try {
      if (interviewId) {
        // Ruta principal: evaluacion estructurada por sesion backend.
        evaluation = await evaluateInterviewSession(interviewId);
      } else {
        if (!transcript || transcript.length === 0) {
          errorMessage = 'No hay transcript para evaluar.';
          return;
        }

        // Respaldo legacy por transcript libre.
        const formattedTranscript = transcript.map((msg) => ({
          role: msg.role,
          content: msg.content
        }));

        const context = `Candidato para puesto de ${config?.jobRole || 'General'}, nivel ${config?.seniority || 'Mid'}. Tipo: ${config?.interviewType || 'Tecnica'}`;
        evaluation = await requestEvaluation(formattedTranscript, context);
      }
    } catch (err) {
      errorMessage = err.message ?? 'Error al evaluar las respuestas.';
    } finally {
      loading = false;
    }
  });

  function backToChat() {
    dispatch('back');
  }

  function openFinalReport() {
    dispatch('continue', { evaluation });
  }
</script>

<section class="evaluation-card">
  <header class="section-header">
    <div>
      <p class="eyebrow">Paso 4</p>
      <h2>Evaluar respuestas</h2>
      <p>
        Analisis automatico de tus respuestas usando inteligencia artificial. Aqui ves fortalezas, areas de mejora y recomendaciones.
      </p>
    </div>
    <div class="config-chip-wrap" aria-label="Estado de la evaluacion">
      <span class="config-chip">{questions.length} preguntas</span>
      <span class="config-chip">
        {loading ? 'Evaluando...' : 'Evaluacion real'}
      </span>
    </div>
  </header>

  {#if loading}
    <div class="evaluation-loading">
      <p>Analizando tus respuestas con IA...</p>
      <div class="spinner"></div>
    </div>
  {:else if errorMessage}
    <div class="evaluation-error">
      <h3>Error en evaluacion</h3>
      <p>{errorMessage}</p>
      <div class="evaluation-actions">
        <button type="button" class="btn-secondary" on:click={backToChat}>Volver al chat</button>
      </div>
    </div>
  {:else if evaluation}
    <div class="evaluation-grid">
      <article class="evaluation-panel evaluation-summary">
        <h3>Resumen ejecutivo</h3>
        <div class="overall-score">
          <span class="score-value">{evaluation.overall_score}</span>
          <span class="score-label">/ 100</span>
        </div>
        <p class="summary-text">{evaluation.summary}</p>
      </article>

      <article class="evaluation-panel evaluation-feedback">
        <h3>Feedback por pregunta</h3>
        <div class="feedback-list">
          {#each evaluation.feedback_items as item}
            <div class="feedback-item">
              <div class="feedback-header">
                <strong>P{item.question_number}: {item.question}</strong>
                <span class="item-score">{item.score}/100</span>
              </div>

              <details class="feedback-details">
                <summary>Tu respuesta</summary>
                <p>{item.answer}</p>
              </details>

              <div class="feedback-section">
                <strong class="section-title">✓ Fortalezas</strong>
                <ul class="strengths-list">
                  {#each item.strengths as strength}
                    <li>{strength}</li>
                  {/each}
                </ul>
              </div>

              <div class="feedback-section">
                <strong class="section-title">△ Areas de mejora</strong>
                <ul class="gaps-list">
                  {#each item.gaps as gap}
                    <li>{gap}</li>
                  {/each}
                </ul>
              </div>

              <div class="feedback-section">
                <strong class="section-title">💡 Recomendacion</strong>
                <p class="recommendation">{item.recommendation}</p>
              </div>
            </div>
          {/each}
        </div>
      </article>
    </div>

    <div class="evaluation-actions">
      <button type="button" class="btn-secondary" on:click={backToChat}>Volver al chat</button>
      <button type="button" class="btn-primary" on:click={openFinalReport}>Ver reporte final</button>
    </div>
  {/if}
</section>

<style>
  .evaluation-card {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
  }

  .section-header > div {
    flex: 1;
  }

  .eyebrow {
    margin: 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .section-header h2 {
    margin: 0.5rem 0 1rem 0;
    font-size: 1.75rem;
    color: #1e293b;
  }

  .section-header p {
    margin: 0;
    color: #64748b;
    line-height: 1.6;
  }

  .config-chip-wrap {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .config-chip {
    padding: 0.5rem 1rem;
    background: #f1f5f9;
    border-radius: 6px;
    font-size: 0.875rem;
    color: #475569;
    font-weight: 500;
  }

  .evaluation-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    padding: 4rem 2rem;
    text-align: center;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e2e8f0;
    border-top-color: #1e7e34;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .evaluation-error {
    padding: 2rem;
    background: #fee2e2;
    border-left: 4px solid #dc2626;
    border-radius: 6px;
  }

  .evaluation-error h3 {
    margin: 0 0 0.5rem 0;
    color: #991b1b;
  }

  .evaluation-error p {
    margin: 0 0 1.5rem 0;
    color: #7f1d1d;
  }

  .evaluation-grid {
    display: grid;
    grid-template-columns: 1fr 1.5fr;
    gap: 2rem;
  }

  .evaluation-panel {
    padding: 1.5rem;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }

  .evaluation-panel h3 {
    margin: 0 0 1rem 0;
    font-size: 1.125rem;
    color: #1e293b;
  }

  .overall-score {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .score-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1e7e34;
  }

  .score-label {
    font-size: 1rem;
    color: #64748b;
  }

  .summary-text {
    margin: 0;
    line-height: 1.6;
    color: #475569;
  }

  .feedback-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .feedback-item {
    padding: 1rem;
    background: white;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
  }

  .feedback-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .feedback-header strong {
    color: #1e293b;
  }

  .item-score {
    padding: 0.25rem 0.75rem;
    background: #dbeafe;
    color: #1e40af;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.875rem;
    white-space: nowrap;
  }

  .feedback-details {
    margin-bottom: 1rem;
    cursor: pointer;
  }

  .feedback-details summary {
    padding: 0.5rem;
    color: #0369a1;
    font-weight: 500;
    user-select: none;
  }

  .feedback-details p {
    margin: 0.5rem 0 0 0;
    padding: 0.5rem;
    background: #ecf0f1;
    border-left: 3px solid #0369a1;
    color: #475569;
    font-size: 0.9rem;
    line-height: 1.5;
  }

  .feedback-section {
    margin-bottom: 0.75rem;
  }

  .section-title {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #475569;
  }

  .strengths-list,
  .gaps-list {
    margin: 0;
    padding-left: 1.5rem;
    list-style: none;
  }

  .strengths-list li::before {
    content: '✓ ';
    color: #16a34a;
    font-weight: 600;
  }

  .gaps-list li::before {
    content: '△ ';
    color: #f59e0b;
    font-weight: 600;
  }

  .strengths-list li,
  .gaps-list li {
    margin-bottom: 0.25rem;
    color: #475569;
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .recommendation {
    margin: 0;
    padding: 0.75rem;
    background: #fef3c7;
    border-left: 3px solid #f59e0b;
    color: #78350f;
    font-size: 0.9rem;
    line-height: 1.5;
    border-radius: 4px;
  }

  .evaluation-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    padding: 2rem 0 0 0;
    border-top: 1px solid #e2e8f0;
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #1e7e34;
    color: white;
  }

  .btn-primary:hover {
    background: #15803d;
  }

  .btn-secondary {
    background: #e2e8f0;
    color: #1e293b;
  }

  .btn-secondary:hover {
    background: #cbd5e1;
  }

  @media (max-width: 768px) {
    .evaluation-grid {
      grid-template-columns: 1fr;
    }

    .feedback-header {
      flex-direction: column;
    }

    .evaluation-actions {
      flex-direction: column;
    }
  }
</style>
