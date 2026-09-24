# Quizambig Technical Specification

## 1. Product

Quizambig is a free quiz platform. Anyone can create a quiz as Quiz Master or participate as a Player.

## 2. Quiz lifecycle

DRAFT -> PUBLISHED -> ACTIVE -> CLOSED -> EVALUATING -> FINALIZED

## 3. Question lifecycle

CREATED -> PUBLISHED -> ACTIVE -> CLOSED -> ANSWER_REVEALED -> EVALUATING -> EVALUATED

## 4. Quiz configuration

Quiz Master controls:
- optional title
- optional description
- required number of questions
- required overall quiz duration in seconds
- question text
- master answer
- evaluation criteria
- optional custom question duration in seconds

Quiz Master does not control:
- semantic threshold
- points per question
- semantic result
- player score
- leaderboard order
- GenLayer validator outcome

## 5. Timing

Overall quiz duration is selected by the Quiz Master in seconds and is the hard upper boundary.

For every question:
answer length -> automatic duration in seconds -> optional custom duration -> final duration.

The final duration is frozen at publication.

The exact automatic timing formula, minimum, and maximum are intentionally not finalized in the prototype.

## 6. Semantic evaluation

The player answer, protected master answer, and evaluation criteria are supplied to a GenLayer non-deterministic semantic evaluation.

The result contains a numeric semantic score.

Rule:
- semantic score >= 60: correct
- semantic score < 60: wrong

The contract stores the accepted semantic result and correctness on the deterministic path after consensus.

## 7. Answer secrecy

The master answer must not be stored as publicly readable plaintext while a question is active.

The production design will use a commitment/reveal or equivalent protected-answer mechanism.

## 8. Speed

Response time is measured from the authoritative question timing mechanism, not trusted solely from frontend click time.

Speed is a scoring component, but correctness and semantic quality remain material. Exact production weighting is not finalized.

## 9. Evaluation UX

10 seconds is a frontend waiting threshold only.

If GenLayer returns within 10 seconds, show the result, update the score/leaderboard, and proceed.

If GenLayer has not returned after 10 seconds, continue immediately, keep evaluation pending, and update the score/leaderboard when the result arrives.

GenLayer evaluation is never cancelled merely because the frontend waited 10 seconds.

## 10. Responsibilities

Deterministic contract logic handles quiz IDs, ownership, question IDs, freeze state, deadlines, player identity, submission rules, duplicate prevention, late-submission prevention, the 60% threshold, score arithmetic, result storage, and finalization.

GenLayer non-deterministic logic handles semantic interpretation/equivalence of natural-language answers.

## 11. Frontend

The frontend will provide landing, shareable quiz links, joining, question screens, visible countdowns, answer submission, post-question master-answer reveal, evaluation status, scores, per-quiz leaderboards, Quiz Master dashboard, creation/publishing, monitoring, and results.

The frontend never determines correctness, score, or leaderboard authority.
