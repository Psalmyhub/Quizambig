# Quizambig Phase 3 — GenLayer Semantic Evaluation

Phase 3 makes GenLayer the authoritative semantic-evaluation layer.

## Evaluation input

GenLayer receives:
- the protected master answer after verified reveal
- the player's submitted answer
- the Quiz Master's evaluation criteria

The prompt explicitly treats those fields as untrusted quiz data so text inside
an answer cannot become an instruction to the evaluator.

## Output

The non-deterministic evaluator returns:

`semantic_score`: integer from 0 through 100

A short explanation is also requested for diagnostics, but the explanation is
not part of the consensus decision.

## Equivalence Principle

Quizambig uses a custom leader/validator pattern.

The leader independently evaluates the answer.

Each validator independently evaluates the same answer.

Validators must:
1. receive a valid 0–100 integer score;
2. agree with the leader on which side of the answer-mode-specific correctness boundary the
   answer belongs;
3. differ from the leader by no more than 5 score points.

This prevents a tolerance window from converting a 59% answer into a 60% answer
or vice versa.

GenLayer's current documentation recommends custom validator logic for
non-deterministic LLM scoring and specifically describes absolute score
tolerance as an appropriate pattern for LLM-generated scores. citeturn1search0turn1search1

## Deterministic result

Only after the Equivalence Principle accepts the result does deterministic
contract code write:

- semantic score
- correctness
- evaluation status

Correctness is then selected from the frozen answer mode:

For TEXT answers:

`semantic_score >= 60 -> correct`

`semantic_score < 60 -> wrong`

For NUMERIC answers:

`semantic_score >= 90 -> correct`

`semantic_score < 90 -> wrong`

The frontend cannot override this result.

## Important boundary

The 60% text / 90% numeric thresholds is an application rule belonging to Quizambig. It is not a
GenLayer protocol-wide threshold. The Equivalence Principle defines how
validators accept the non-deterministic evaluation; Quizambig's deterministic
code applies the 60% rule afterward. citeturn0search0turn0search1

## Deterministic storage

No contract storage is mutated inside the non-deterministic leader/validator
functions. Storage is updated only after the accepted result returns to the
deterministic contract path, consistent with GenLayer's current execution
rules. citeturn1search4

## Phase 3 status

Implemented:
- evaluation state
- semantic score storage
- 60% correctness threshold
- custom Equivalence Principle validator
- score tolerance
- correctness-boundary protection
- deterministic result persistence
- evaluation read methods

Next:
- execute the full GenLayer test suite
- test validator disagreement and retries
- define the final pending-evaluation lifecycle
- connect semantic results to speed-aware scoring
- build the per-quiz leaderboard


## Answer mode and thresholds

Each published question has an immutable answer mode:

- `TEXT`: 60% semantic-score threshold.
- `NUMERIC`: 90% semantic-score threshold.

The mode is supplied when the question is created and is bound into the
master-answer commitment. It cannot be changed after publication.

For numeric questions, GenLayer is instructed to recognize equivalent numeric
forms, including number words. For example, for `2 + 2`, a master answer of
`4` can semantically match `four`. A numerically close but materially
different value must meet the stricter 90% threshold.

The 10-second frontend evaluation threshold remains a UX threshold only; it
does not cancel or invalidate GenLayer evaluation.
