# Quizambig

Quizambig is a free semantic quiz platform built on GenLayer.

## Core idea

Quiz Masters publish quizzes containing questions, protected master answers, evaluation criteria, and timing. Players answer naturally in their own words. GenLayer evaluates semantic equivalence and produces an authoritative semantic score.

### Locked product rules

- Quiz title and description are optional.
- Quiz Master chooses the overall quiz duration in seconds.
- Each question gets an automatic duration derived from master-answer length.
- Quiz Master may override the automatically derived question duration in seconds.
- Question timing is frozen when the quiz is published.
- Quiz Master cannot assign per-question points.
- Semantic score below 60% is wrong; 60% or above is correct.
- Speed contributes to the system-generated score without replacing correctness.
- Master answers are not publicly revealed while a question is active.
- GenLayer is authoritative for semantic evaluation.
- The frontend displays authoritative contract results; it does not decide correctness or score.
- A 10-second frontend waiting threshold controls UX only. It does not cancel GenLayer evaluation.
- If evaluation takes longer than 10 seconds, the player continues to the next question while the evaluation remains pending and later updates the leaderboard.

## Initial milestone

Create Quiz -> Add Questions -> Freeze -> Submit Answer -> Close Question -> Reveal Answer -> GenLayer Semantic Evaluation -> 60% Result.

The exact production scoring formula and automatic timing formula will be finalized before production release.

## Architecture

- contracts/ — GenLayer Intelligent Contracts
- tests/ — contract behavior tests
- docs/ — product and technical specifications

## GenLayer

Quizambig uses GenLayer's Equivalence Principle for non-deterministic semantic evaluation. Consensus accepts a proposed result only when validators accept it under the contract-defined equivalence rule.

See the current GenLayer documentation at https://docs.genlayer.com/.
