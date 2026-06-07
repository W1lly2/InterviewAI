<script>
  export let stages = [];
  export let currentStep = 1;
</script>

<div class="stage-flow" aria-label="Flujo de entrevista">
  {#each stages as stage, index}
    <div class="stage-item {currentStep === index + 1 ? 'is-current' : ''}">
      <span class="stage-number">{index + 1}</span>
      <span class="stage-label">{stage}</span>
    </div>
  {/each}
</div>
