# Quizambig Phase 1 — Deterministic Quiz Model

This phase establishes the persistent state and lifecycle before adding
GenLayer semantic evaluation.

## Implemented model

### Quiz
- Quiz Master
- optional title
- optional description
- required question count
- overall duration in seconds
- creation timestamp
- publication timestamp
- lifecycle status

### Question
- question text
- protected answer commitment
- master-answer length
- evaluation criteria
- automatic time
- optional custom time
- final time
- lifecycle status

## Timing

Prototype rule:

`automatic_time = master_answer_length`

This is a temporary, explicit prototype formula. It is **not** the final
production timing formula.

If a custom time is supplied:

`final_time = custom_time`

Otherwise:

`final_time = automatic_time`

Publishing freezes these values.

## Publication rule

A quiz cannot publish until its required number of questions exists.

After publication:
- quiz configuration is frozen
- question text is frozen
- answer commitment is frozen
- evaluation criteria are frozen
- final timing is frozen

## Security note

The answer is represented by a commitment rather than plaintext in the active
question state. The next implementation phase must add a cryptographically
verified reveal path. We will not treat an unverified plaintext reveal as
production-safe.

## Next implementation phase

1. Cryptographic commitment/reveal
2. Player registration
3. Submission deadlines
4. Duplicate-submission prevention
5. Question closure
6. Master-answer reveal
7. GenLayer semantic evaluation using the Equivalence Principle
8. 60% correctness threshold
