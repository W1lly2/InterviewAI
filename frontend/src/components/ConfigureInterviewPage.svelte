<script>
  import { createEventDispatcher } from 'svelte';

  export let config;
  export let jobRoles = [];
  export let seniorityLevels = [];
  export let interviewTypes = [];

  const dispatch = createEventDispatcher();

  function handleSubmit(event) {
    event.preventDefault();
    dispatch('continue');
  }
</script>

<section class="configure-card">
  <header>
    <h2>Configurar entrevista</h2>
    <p>Define contexto y dificultad antes de iniciar la simulacion.</p>
  </header>

  <form class="configure-grid" on:submit={handleSubmit}>
    <label>
      Puesto objetivo
      <select name="job-role" bind:value={config.jobRole}>
        {#each jobRoles as role}
          <option value={role}>{role}</option>
        {/each}
      </select>
    </label>

    <label>
      Seniority
      <select name="seniority" bind:value={config.seniority}>
        {#each seniorityLevels as level}
          <option value={level}>{level}</option>
        {/each}
      </select>
    </label>

    <label>
      Tipo de entrevista
      <select name="interview-type" bind:value={config.interviewType}>
        {#each interviewTypes as type}
          <option value={type}>{type}</option>
        {/each}
      </select>
    </label>

    <label>
      Duracion estimada (minutos)
      <input type="number" min="15" max="90" bind:value={config.duration} />
    </label>

    <label class="full-width">
      Stack o habilidades clave
      <input type="text" bind:value={config.stack} placeholder="Ej: Svelte, FastAPI, SQL, Testing" />
    </label>

    <label class="full-width">
      Contexto adicional
      <textarea
        rows="4"
        bind:value={config.context}
        placeholder="Ej: Quiero practicar arquitectura, comunicacion tecnica y manejo de trade-offs."
      ></textarea>
    </label>

    <div class="cta-row full-width">
      <button type="button" class="btn-secondary">Guardar borrador</button>
      <button type="submit" class="btn-primary">Generar preguntas</button>
    </div>
  </form>
</section>
