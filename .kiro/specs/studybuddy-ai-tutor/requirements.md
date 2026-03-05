# Requirements Document — StudyBuddy AI

## Introduction

StudyBuddy AI is the transformation of a generic chatbot template (AgentCore Chatbot) into a 24/7 intelligent tutor aimed at students. The goal is to customize both the backend (agent prompt and behavior) and the frontend (branding, colors, chat experience) to create a complete educational experience, ready to be presented at AWS Student Community Day.

## Glossary

- **Agent**: The backend component based on Strands Agent that processes student queries and generates educational responses using Amazon Bedrock.
- **System_Prompt**: The system instruction that defines the personality, tone, and behavior of the Agent.
- **Frontend**: The React/TypeScript application that presents the user interface to the Student.
- **Student**: The end user who interacts with StudyBuddy AI to learn.
- **Home_Page**: The initial view (Home) that the Student sees upon entering the application.
- **Chat_View**: The conversation component where the Student interacts with the Agent.
- **Login_Page**: The sign-in view where the Student authenticates.
- **Signup_Page**: The registration view where the Student creates an account.
- **Navigation**: The interface elements that allow the Student to move between the application views.
- **Suggested_Topics**: Examples of educational questions shown to the Student to start a conversation.

## Requirements

### Requirement 1: Configure the Educational Tutor System Prompt

**User Story:** As a student, I want the chatbot to behave like a patient and friendly educational tutor, so that it helps me understand concepts in a clear and structured way.

#### Acceptance Criteria

1. THE System_Prompt SHALL instruct the Agent to explain concepts in simple and clear language.
2. THE System_Prompt SHALL instruct the Agent to break down explanations into steps or bullet points.
3. THE System_Prompt SHALL instruct the Agent to use concrete examples to help visualize concepts.
4. THE System_Prompt SHALL instruct the Agent to start with simple explanations and progressively add detail for complex questions.
5. THE System_Prompt SHALL instruct the Agent to encourage curiosity and continuous learning in the Student.
6. THE System_Prompt SHALL instruct the Agent to offer to create practice questions, summaries, or quizzes when relevant.
7. THE System_Prompt SHALL instruct the Agent to maintain a friendly, supportive, encouraging, and patient tone.
8. THE System_Prompt SHALL instruct the Agent to structure responses with headings, bullet points, and Markdown formatting.
9. WHEN the Student asks a question unrelated to educational topics, THE Agent SHALL redirect the conversation back to learning in a friendly manner.
10. THE System_Prompt SHALL be written in Spanish to align with the AWS Student Community Day audience.

### Requirement 2: Update Frontend Branding to StudyBuddy AI

**User Story:** As a student, I want the application to have StudyBuddy AI visual branding, so that the experience is consistent with the intelligent tutor identity.

#### Acceptance Criteria

1. THE Frontend SHALL display the title "StudyBuddy AI" instead of "AgentCore Chatbot" on the Home_Page, Chat_View, Login_Page, Signup_Page, and Navigation.
2. THE Frontend SHALL display the subtitle "Tu tutor inteligente 24/7" on the Home_Page.
3. THE Frontend SHALL use the StudyBuddy AI logo (owl robot reading a book) as the favicon and on the Home_Page.
4. THE Frontend SHALL display "StudyBuddy AI" as the browser tab title in the main HTML file.
5. THE Frontend SHALL apply an educational color palette consistent with the StudyBuddy AI brand, replacing the current orange/navy palette from the generic template.

### Requirement 3: Customize the Home Page for Educational Use

**User Story:** As a student, I want the home page to invite me to learn and suggest educational topics, so that I know how to make the most of the tutor.

#### Acceptance Criteria

1. THE Home_Page SHALL display a learning-oriented welcome message instead of the current generic message.
2. THE Home_Page SHALL display the StudyBuddy AI logo prominently in the header.
3. THE Home_Page SHALL display Suggested_Topics relevant to students, replacing the current generic examples.
4. WHEN the Student selects a Suggested_Topics item, THE Home_Page SHALL load the topic text into the text input field.
5. THE Home_Page SHALL display a placeholder in the text input field with text that invites the Student to ask educational questions.

### Requirement 4: Customize the Chat View for the Educational Experience

**User Story:** As a student, I want the chat interface to reflect that I am interacting with an educational tutor, so that the experience is immersive and motivating.

#### Acceptance Criteria

1. THE Chat_View SHALL display "StudyBuddy AI" as the chat header title instead of "AgentCore Chatbot (WebSocket)".
2. THE Chat_View SHALL display an educational placeholder in the text input field when the WebSocket connection is active.
3. WHILE the Agent processes a query, THE Chat_View SHALL display a loading indicator with educational contextual text instead of the generic "Thinking..." text.

### Requirement 5: Customize the Authentication Pages

**User Story:** As a student, I want the login and signup pages to reflect the StudyBuddy AI brand, so that the experience is consistent from the first interaction.

#### Acceptance Criteria

1. THE Login_Page SHALL display "StudyBuddy AI" as the brand and a learning-oriented welcome message instead of "Welcome Back" and "AgentCore Chat".
2. THE Signup_Page SHALL display "StudyBuddy AI" as the brand and a learning invitation message instead of "Create Account" and "AgentCore Chat".
