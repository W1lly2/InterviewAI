// Genera un set de preguntas mock para simular la experiencia antes del backend real.
export function buildQuestionSet({ config, questionBlueprints, count = 6 }) {
  const source = questionBlueprints[config.interviewType] || questionBlueprints.Mixta;
  const tags = config.stack
    .split(',')
    .map((skill) => skill.trim())
    .filter(Boolean);

  return Array.from({ length: count }, (_, idx) => {
    const item = source[idx % source.length];
    const focus = tags[idx % Math.max(tags.length, 1)] || config.jobRole;

    return {
      ...item,
      prompt: `${item.prompt} Enfoca tu respuesta en ${focus}.`
    };
  });
}
