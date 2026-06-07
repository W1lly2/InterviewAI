<script>
  import StageFlow from './StageFlow.svelte';

  export let stages = [];
  export let currentStep = 1;
</script>

<section class="hero-card">
  <p class="eyebrow">InterviewAI Simulator</p>
  <h1>Entrena entrevistas reales con una IA que te reta y te evalua</h1>
  <p class="lead">
    Configura el puesto, genera preguntas personalizadas y recibe un reporte final con fortalezas,
    brechas y recomendaciones accionables.
  </p>

  <StageFlow stages={stages} currentStep={currentStep} />
</section>
