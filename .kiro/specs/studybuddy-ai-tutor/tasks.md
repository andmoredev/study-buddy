# Implementation Plan: StudyBuddy AI Tutor

## Overview

Transform the AgentCore Chatbot template into StudyBuddy AI by replacing the backend system prompt with a Spanish educational tutor prompt, rebranding all frontend components, updating the color palette, and adding new logo/favicon assets. Implementation proceeds backend-first, then frontend assets, then component-by-component UI updates, with tests wired in alongside each change.

## Tasks

- [x] 1. Replace the backend system prompt with the Spanish educational tutor prompt
  - [x] 1.1 Update `SYSTEM_PROMPT` in `backend/agents/agent/agent.py`
    - Replace the existing `SYSTEM_PROMPT` string with the new Spanish educational tutor prompt
    - The prompt must instruct the agent to: explain in simple language, use step-by-step breakdowns, provide concrete examples, start simple and add detail progressively, encourage curiosity, offer practice questions/quizzes/summaries, maintain a friendly and patient tone, use Markdown formatting, and redirect off-topic questions back to learning
    - The entire prompt must be written in Spanish
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10_

  - [ ]* 1.2 Write property test: System prompt contains all required educational instructions (Property 1)
    - **Property 1: System prompt contains all required educational instructions**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9**
    - Use hypothesis to generate random subsets of required instructional topics and verify each is addressed in `SYSTEM_PROMPT`
    - Create test file `backend/tests/test_system_prompt_properties.py`

  - [ ]* 1.3 Write property test: System prompt is written in Spanish (Property 2)
    - **Property 2: System prompt is written in Spanish**
    - **Validates: Requirements 1.10**
    - Verify the prompt does not contain English-only structural phrases and contains Spanish keywords
    - Add to `backend/tests/test_system_prompt_properties.py`

- [x] 2. Checkpoint - Verify backend changes
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Add frontend assets and update index.html
  - [x] 3.1 Create `frontend/public/studybuddy-favicon.svg`
    - Add a simplified owl icon SVG for the browser tab favicon
    - _Requirements: 2.3_

  - [x] 3.2 Create `frontend/public/studybuddy-logo.svg`
    - Add the full owl-robot-reading-a-book logo SVG for the Home page
    - _Requirements: 2.3_

  - [x] 3.3 Update `frontend/index.html`
    - Change `<title>` from "AgentCore Chatbot" to "StudyBuddy AI"
    - Change favicon `<link>` href from "/vite.svg" to "/studybuddy-favicon.svg"
    - _Requirements: 2.4, 2.3_

- [x] 4. Update the color palette
  - [x] 4.1 Replace CSS custom properties in `frontend/src/index.css`
    - Replace `--primary: #FF6B35` and related orange values with the new educational green palette
    - Set `--primary: #4CAF50`, `--primary-hover: #388E3C`, `--primary-light: rgba(76, 175, 80, 0.1)`, `--accent: #FFB74D`, and the navy/teal background variables as specified in the design
    - _Requirements: 2.5_

  - [x] 4.2 Update gradient and accent colors in `frontend/src/components/Auth.css`
    - Replace the purple gradient (`#667eea → #764ba2`) with the educational green/teal gradient
    - _Requirements: 2.5_

  - [x] 4.3 Update color references in `frontend/src/App.css`
    - Replace any remaining old color references with the new educational palette values
    - _Requirements: 2.5_

  - [ ]* 4.4 Write property test: Old color palette is fully replaced (Property 4)
    - **Property 4: Old color palette is fully replaced**
    - **Validates: Requirements 2.5**
    - Scan `index.css` and `Auth.css` for old color value `#FF6B35`, verify it does not appear, and verify new palette values are present
    - Create test file `frontend/src/__tests__/colorPalette.property.test.ts` using fast-check

- [x] 5. Update frontend components with StudyBuddy AI branding
  - [x] 5.1 Update `frontend/src/components/Home.tsx`
    - Change title from "AgentCore Chatbot" to "StudyBuddy AI"
    - Change subtitle from "Ask me anything - I'm here to help" to "Tu tutor inteligente 24/7"
    - Add StudyBuddy AI owl logo (`<img src="/studybuddy-logo.svg">`) above the title
    - Change input placeholder from "What would you like to know?" to "¿Qué tema quieres aprender hoy?"
    - Replace suggested topics with educational ones: "Explícame el ciclo del agua paso a paso", "¿Cuáles son las leyes de Newton?", "Ayúdame a entender las fracciones con ejemplos"
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 5.2 Update `frontend/src/components/Chat.tsx`
    - Change header title from "AgentCore Chatbot (WebSocket)" to "StudyBuddy AI"
    - Change connected input placeholder from "Type your message..." to "Escribe tu pregunta aquí..."
    - Change loading text from "Thinking..." to "Buscando la mejor explicación..."
    - _Requirements: 2.1, 4.1, 4.2, 4.3_

  - [x] 5.3 Update `frontend/src/components/Login.tsx`
    - Change heading from "Welcome Back" to "StudyBuddy AI"
    - Change subtitle from "Sign in to continue to AgentCore Chat" to "Inicia sesión para seguir aprendiendo"
    - _Requirements: 2.1, 5.1_

  - [x] 5.4 Update `frontend/src/components/Signup.tsx`
    - Change heading from "Create Account" to "StudyBuddy AI"
    - Change subtitle from "Sign up to start using AgentCore Chat" to "Crea tu cuenta y comienza a aprender"
    - _Requirements: 2.1, 5.2_

  - [x] 5.5 Update `frontend/src/components/Navigation.tsx`
    - Change brand name from "AgentCore Chatbot" to "StudyBuddy AI"
    - _Requirements: 2.1_

  - [ ]* 5.6 Write property test: No old template branding remains in frontend components (Property 3)
    - **Property 3: No old template branding remains in frontend components**
    - **Validates: Requirements 2.1, 4.1, 5.1, 5.2**
    - For each component file in {Home.tsx, Chat.tsx, Login.tsx, Signup.tsx, Navigation.tsx, index.html}, verify absence of "AgentCore Chatbot" and "AgentCore Chat" strings, and verify presence of "StudyBuddy AI"
    - Create test file `frontend/src/__tests__/branding.property.test.ts` using fast-check

  - [ ]* 5.7 Write property test: Suggested topics are educational (Property 5)
    - **Property 5: Suggested topics are educational**
    - **Validates: Requirements 3.3**
    - Verify none of the old generic topics remain ("What can you help me with?", "Explain how to get started with AWS Bedrock", "Help me brainstorm ideas for my project") and the new educational topics are present in Home.tsx
    - Add to `frontend/src/__tests__/branding.property.test.ts` using fast-check

- [x] 6. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests use fast-check (TypeScript) and hypothesis (Python) as specified in the design
- Backend and frontend changes are independent and can be developed in parallel, but the task order ensures backend is validated first
