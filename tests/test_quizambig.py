"""Phase-2 behavior checklist.

The repository will wire these scenarios into the GenLayer test runner next.
The checklist is intentionally explicit so no phase-2 rule is lost.

Required tests:
- quiz cannot publish before all questions exist
- player can join a published quiz before expiry
- player cannot join twice
- player cannot join after overall expiry
- only joined players can submit
- only one submission per player/question
- submission after question deadline is rejected
- response time is recorded from contract question start
- question deadline cannot extend beyond overall quiz expiry
- question cannot be started after overall expiry
- question cannot be closed before its deadline
- master answer cannot be revealed before question closure
- incorrect answer/salt cannot reveal the master answer
- correct commitment reveals the master answer
- master answer remains unavailable through the public reveal view until verified reveal
- published quiz/question configuration cannot be edited
