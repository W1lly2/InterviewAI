// Catalogos base del dominio de entrevistas para reutilizar en toda la app.
export const interviewStages = [
  'Configurar entrevista',
  'Generar preguntas',
  'Chat con IA',
  'Evaluar respuestas',
  'Reporte final'
];

export const jobRoles = [
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'Data Analyst',
  'Product Manager'
];

export const seniorityLevels = ['Junior', 'Semi Senior', 'Senior', 'Lead'];

export const interviewTypes = ['Tecnica', 'Conductual', 'Mixta'];

export const questionBlueprints = {
  Tecnica: [
    {
      category: 'Arquitectura',
      title: 'Disena una solucion escalable',
      prompt: 'Si tuvieras que soportar un pico de usuarios x10 en una hora, como redisenarias la arquitectura y que trade-offs aceptarias?'
    },
    {
      category: 'Codigo',
      title: 'Refactor orientado a mantenibilidad',
      prompt: 'Describe un caso real donde simplificaste una base de codigo compleja sin romper funcionalidad critica.'
    },
    {
      category: 'Testing',
      title: 'Estrategia de pruebas por riesgo',
      prompt: 'Como decides que pruebas automatizar primero cuando tienes poco tiempo y muchas historias pendientes?'
    }
  ],
  Conductual: [
    {
      category: 'Comunicacion',
      title: 'Explicar decisiones dificiles',
      prompt: 'Cuentame una decision tecnica impopular que defendiste. Como lograste alinear al equipo?'
    },
    {
      category: 'Liderazgo',
      title: 'Gestion de conflicto',
      prompt: 'Describe un conflicto con otro perfil tecnico y como lo resolviste sin frenar la entrega.'
    },
    {
      category: 'Impacto',
      title: 'Medicion de resultados',
      prompt: 'Como demuestras que una mejora propuesta por ti realmente genero valor para negocio?'
    }
  ],
  Mixta: [
    {
      category: 'Sistema',
      title: 'Priorizacion tecnica y de negocio',
      prompt: 'Tienes deuda tecnica alta y una fecha comercial cercana. Como decides que resolver primero y por que?'
    },
    {
      category: 'Colaboracion',
      title: 'Trabajo con producto',
      prompt: 'Como conviertes un requerimiento ambiguo en criterios de aceptacion tecnicos claros?'
    },
    {
      category: 'Resolucion',
      title: 'Debugging bajo presion',
      prompt: 'En produccion aparece un bug intermitente. Cual es tu plan en los primeros 30 minutos?'
    }
  ]
};
