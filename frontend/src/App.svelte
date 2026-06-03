<script>
  // Datos base para renderizar las etapas del proceso de entrevista.
  const interviewStages = [
    'Configurar entrevista',
    'Generar preguntas',
    'Chat con IA',
    'Evaluar respuestas',
    'Reporte final'
  ];

  // Opciones de ejemplo para el formulario de configuracion.
  const jobRoles = [
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
    'Data Analyst',
    'Product Manager'
  ];

  const seniorityLevels = ['Junior', 'Semi Senior', 'Senior', 'Lead'];
  const interviewTypes = ['Tecnica', 'Conductual', 'Mixta'];
</script>

<main class="page-shell">
  <section class="hero-card">
    <p class="eyebrow">InterviewAI Simulator</p>
    <h1>Entrena entrevistas reales con una IA que te reta y te evalua</h1>
    <p class="lead">
      Configura el puesto, genera preguntas personalizadas y recibe un reporte final con fortalezas,
      brechas y recomendaciones accionables.
    </p>

    <div class="stage-flow" aria-label="Flujo de entrevista">
      {#each interviewStages as stage, index}
        <div class="stage-item">
          <span class="stage-number">{index + 1}</span>
          <span class="stage-label">{stage}</span>
        </div>
      {/each}
    </div>
  </section>

  <section class="configure-card">
    <header>
      <h2>Configurar entrevista</h2>
      <p>Define contexto y dificultad antes de iniciar la simulacion.</p>
    </header>

    <form class="configure-grid">
      <label>
        Puesto objetivo
        <select name="job-role">
          {#each jobRoles as role}
            <option value={role}>{role}</option>
          {/each}
        </select>
      </label>

      <label>
        Seniority
        <select name="seniority">
          {#each seniorityLevels as level}
            <option value={level}>{level}</option>
          {/each}
        </select>
      </label>

      <label>
        Tipo de entrevista
        <select name="interview-type">
          {#each interviewTypes as type}
            <option value={type}>{type}</option>
          {/each}
        </select>
      </label>

      <label>
        Duracion estimada (minutos)
        <input type="number" min="15" max="90" value="35" />
      </label>

      <label class="full-width">
        Stack o habilidades clave
        <input type="text" placeholder="Ej: Svelte, FastAPI, SQL, Testing" />
      </label>

      <label class="full-width">
        Contexto adicional
        <textarea rows="4" placeholder="Ej: Quiero practicar arquitectura, comunicacion tecnica y manejo de trade-offs."></textarea>
      </label>

      <div class="cta-row full-width">
        <button type="button" class="btn-secondary">Guardar borrador</button>
        <button type="submit" class="btn-primary">Generar preguntas</button>
      </div>
    </form>
  </section>
</main>
