# Quizambig Phase 2 — Player Submission and Answer Protection

Phase 2 adds the authoritative player/question flow while keeping semantic
evaluation for Phase 3.

## Commitment format

The Quiz Master creates a commitment off-chain:

SHA-256(UTF-8(answer + ":" + salt))

The contract stores only the 64-character lowercase hexadecimal digest.

The plaintext master answer is not stored while the question is active.

## Player flow

PUBLISHED
-> join_quiz()
-> ACTIVE
-> start_question()
-> submit_answer()
-> close_question()
-> reveal_master_answer()

## Joining

A player:
- must join while the quiz is PUBLISHED
- must join before the overall quiz expiry
- can join only once per quiz

The first successful join changes the quiz to ACTIVE.

## Submission

A player:
- must have joined the quiz
- must submit while the question is ACTIVE
- must submit by the authoritative contract deadline
- may submit only once per question

The contract stores:
- answer
- submitted timestamp
- response time in seconds

The frontend timestamp is not authoritative.

## Question timing

At question start:

question_deadline = question_start + final_time

The deadline is capped at the quiz's overall expiry.

## Closure

The Quiz Master closes the question after its deadline.

Phase 2 does not yet include automatic state transitions caused by a background
worker. The state transition is explicit and deterministic.

## Answer reveal

The Quiz Master supplies:
- plaintext master answer
- secret salt

The contract recomputes SHA-256(answer + ":" + salt) and requires it to equal
the stored commitment.

Only after successful verification is the answer stored as revealed and made
available through get_revealed_answer().

## Security boundary

During an active question, the public question view exposes the commitment
and question metadata but not the plaintext master answer.

The commitment must be generated from a sufficiently secret salt. The
production frontend must never expose the salt before reveal.

## Phase 3

Phase 3 will add GenLayer semantic evaluation using the Equivalence Principle.
The non-deterministic evaluation will be isolated from deterministic storage
writes, consistent with GenLayer's current execution model.
