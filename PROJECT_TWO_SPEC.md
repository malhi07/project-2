# PROJECT TWO — Build Specification for Claude Code

## OVERVIEW
Build a free, open-source, all-in-one English proficiency practice platform
(personal project, not for commercial use) modeled on the functional
structure of CELPIP-style exam prep tools. This is an original build:
use original branding, original UI design, and original written content.
Do NOT copy any text, images, or code from third-party commercial sites.
Only the *functional concept* below should be replicated.

## TECH STACK SUGGESTION
- Frontend: React with Tailwind CSS
- Backend: Node.js / Express or Python FastAPI
- Database: PostgreSQL for user data, scores, and question banks
- AI: Claude API for Writing/Speaking scoring and feedback generation
- Speech: Web Speech API or a speech-to-text service for Speaking responses
- Auth: simple email/password or OAuth for user accounts
- Hosting target: Vercel/Render, repo on GitHub named "project-two"

## CORE MODULES

### 1. Diagnostic Placement Test
- Short adaptive test (15–20 min) covering all 4 skills at a basic level
- Outputs an estimated starting CLB band (1–12) per skill
- Used to seed the personalized study plan

### 2. Listening Practice
- Audio-based multiple choice questions, single-play only (no replay) in "exam mode", replay allowed in "practice mode"
- Raw score out of N questions converts to CLB level via a scoring table
  (approx: 27/38 correct maps to CLB 7, 30/38 to CLB 8, 33/38 to CLB 9 —
  use a configurable score-to-CLB mapping table, not hardcoded, since
  real conversion varies by test version)
- Full transcript and answer key shown only in practice mode, never in exam mode

### 3. Reading Practice
- Multiple choice reading comprehension questions across varied text types
  (emails, diagrams, opinion pieces, viewpoints)
- Same raw-score-to-CLB conversion approach as Listening
- Timed exam mode and untimed practice mode

### 4. Writing Practice and AI Scoring
- Two task types: short functional writing (email/message) and
  opinion/survey response writing
- Built-in timers matching real exam pacing (e.g., ~27 min task 1,
  ~26 min task 2), configurable
- AI scoring engine (via Claude API) rates each response on four
  rating dimensions:
  - a. Content and Coherence
  - b. Vocabulary
  - c. Readability
  - d. Task Fulfillment
- Each dimension scored individually (1–12 CLB scale) then combined
  into an overall band
- **Detailed feedback requirement:**
  - Inline error highlighting: mark specific words/sentences where marks were lost
  - For each flagged issue, explain WHY it lost marks (which dimension/rubric criterion it violates)
  - Show a corrected or improved rewrite of the flawed sentence/section
  - Summarize overall "what would move you up one CLB level" advice
- Sample answers shown at multiple CLB levels for comparison after submission

### 5. Speaking Practice and AI Scoring
- 8 original speaking task types (giving advice, describing a scenario,
  expressing opinions, comparing/persuading, describing an unusual
  situation, etc. — use original task framing)
- Timed prep + response recording per task
- AI scoring on four dimensions: Content/Coherence, Vocabulary,
  Listenability, Task Fulfillment
- **Pronunciation and fluency checker:**
  - Speech-to-text transcription of the response
  - Analysis of pace (words per minute), filler words, pauses, and pronunciation clarity where feasible
  - Feedback separate from content scoring, framed as delivery tips
- Detailed feedback following same "what lost marks and why, plus improved example" format as Writing

### 6. Vocabulary Practice Module (standalone from mock exams)
- Word-of-the-day and themed vocabulary sets (e.g., workplace,
  immigration, daily life, opinions/argumentation)
- Synonym/antonym matching exercises
- Fill-in-the-blank sentence exercises using target words
- Spaced repetition system (SRS) so words a user gets wrong resurface more frequently
- Difficulty levels aligned loosely to CLB bands (e.g., CLB 4–6, 7–9, 10–12)

### 7. Progress Dashboard
- Score history charts per skill over time (Listening, Reading, Writing, Speaking)
- CLB band trend line and best/average/last score per skill
- Breakdown by rubric dimension for Writing/Speaking to show which specific criterion is the weakest over time
- Vocabulary mastery tracker (words learned, words due for review)

### 8. Personalized Study Plan Generator
- Uses diagnostic test results plus ongoing performance data
- Suggests a weekly practice schedule prioritizing weakest skills and weakest rubric dimensions
- Adjusts recommendations as new practice results come in

## Scoring Accuracy Requirement
- All CLB-mapping logic, rubric dimensions, and score conversion tables
  should be stored in a clearly separated, editable config/data file
  (not hardcoded across the app), so scoring can be corrected or
  calibrated against publicly available official CLB descriptor
  documents without touching core app logic.
- Cite that scoring dimensions are based on publicly documented CLB
  (Canadian Language Benchmark) descriptors: Content/Coherence,
  Vocabulary, Readability/Listenability, and Task Fulfillment.

## Access and Cost
- Entire platform free for all users, no paywalls
- Consider rate-limiting AI scoring calls per user per day to manage API costs, but do not gate core features behind payment

## Deliverable Structure for Claude Code
- Repo name: `project-two`
- Please scaffold: `/frontend`, `/backend`, `/data` (scoring configs and question bank schemas), `/docs` (setup instructions)
- Include a README explaining setup, environment variables needed (e.g., `ANTHROPIC_API_KEY`), and how to run locally
- Build incrementally: start with data models and one full vertical slice (e.g., Writing practice + AI scoring + feedback) before expanding to all modules
