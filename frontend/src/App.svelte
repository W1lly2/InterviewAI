<script>
  import ChatPage from './components/ChatPage.svelte';
  import ConfigureInterviewPage from './components/ConfigureInterviewPage.svelte';
  import EvaluationSimulationPage from './components/EvaluationSimulationPage.svelte';
  import FinalReportPage from './components/FinalReportPage.svelte';
  import GenerateQuestionsPage from './components/GenerateQuestionsPage.svelte';
  import HeroOverview from './components/HeroOverview.svelte';
  import {
    interviewStages,
    interviewTypes,
    jobRoles,
    questionBlueprints,
    seniorityLevels
  } from './modules/interview/catalog.js';
  import { buildQuestionSet } from './modules/interview/questionGenerator.js';
  import { createInitialInterviewConfig } from './modules/interview/state.js';

  let currentStep = 1;
  let generatedQuestions = [];
  let chatTranscript = [];
  let interviewSessionId = null;
  let evaluationResult = null;

  let interviewConfig = createInitialInterviewConfig({
    jobRoles,
    seniorityLevels,
    interviewTypes
  });

  function generateQuestions(count = 6) {
    generatedQuestions = buildQuestionSet({
      config: interviewConfig,
      questionBlueprints,
      count
    });
  }

  function goToQuestionGeneration() {
    generateQuestions();
    interviewSessionId = null;
    evaluationResult = null;
    currentStep = 2;
  }

  function goToChatPhase() {
    currentStep = 3;
  }

  function goToEvaluationPhase(event) {
    interviewSessionId = event?.detail?.interviewId ?? null;
    chatTranscript = event.detail.transcript || [];
    currentStep = 4;
  }

  function goToFinalReport(event) {
    evaluationResult = event?.detail?.evaluation ?? null;
    currentStep = 5;
  }
</script>

<main class="page-shell">
  <HeroOverview stages={interviewStages} currentStep={currentStep} />

  {#if currentStep === 1}
    <ConfigureInterviewPage
      config={interviewConfig}
      jobRoles={jobRoles}
      seniorityLevels={seniorityLevels}
      interviewTypes={interviewTypes}
      on:continue={goToQuestionGeneration}
    />
  {:else if currentStep === 2}
    <GenerateQuestionsPage
      config={interviewConfig}
      questions={generatedQuestions}
      on:regenerate={() => generateQuestions()}
      on:continue={goToChatPhase}
    />
  {:else if currentStep === 3}
    <ChatPage
      config={interviewConfig}
      questions={generatedQuestions}
      on:back={goToQuestionGeneration}
      on:continue={goToEvaluationPhase}
    />
  {:else if currentStep === 4}
    <EvaluationSimulationPage
      config={interviewConfig}
      questions={generatedQuestions}
      interviewId={interviewSessionId}
      transcript={chatTranscript}
      on:back={() => (currentStep = 3)}
      on:continue={goToFinalReport}
    />
  {:else}
    <FinalReportPage
      evaluation={evaluationResult}
      questions={generatedQuestions}
      config={interviewConfig}
      on:back={() => (currentStep = 4)}
      on:restart={() => {
        interviewSessionId = null;
        evaluationResult = null;
        currentStep = 1;
      }}
    />
  {/if}
</main>
