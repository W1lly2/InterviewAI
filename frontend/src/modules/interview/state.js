// Crea el estado inicial del formulario sin acoplarlo a App.svelte.
export function createInitialInterviewConfig({ jobRoles, seniorityLevels, interviewTypes }) {
  return {
    jobRole: jobRoles[0],
    seniority: seniorityLevels[1],
    interviewType: interviewTypes[2],
    duration: 35,
    stack: 'Svelte, FastAPI, SQL, Testing',
    context: 'Quiero practicar arquitectura, comunicacion tecnica y manejo de trade-offs.'
  };
}
