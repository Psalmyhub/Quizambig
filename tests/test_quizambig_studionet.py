"""Live Quizambig integration test.

This test intentionally exercises the real GenLayer Studionet path:

    deploy -> create quiz -> add question -> publish -> join ->
    start -> submit -> close -> reveal -> nondeterministic evaluation.

Run explicitly on Studionet:

    gltest --network studionet tests/test_quizambig_studionet.py -v -s

Important:
- gltest Studio-mode write methods are called with args=[...].
- .transact() returns a transaction receipt, not the contract method's
  Python return value. IDs are therefore captured from the corresponding
  next-id view before the write transaction.
- The evaluation transaction is the real nondeterministic GenLayer path.
"""

import hashlib
import time

from gltest.assertions import tx_execution_succeeded
from gltest.contracts.contract_factory import get_contract_factory


def make_commitment(answer: str, salt: str, answer_mode: str) -> str:
    """Match Quizambig's on-chain answer commitment formula."""
    payload = f"{answer}:{salt}:{answer_mode}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def assert_success(receipt, step: str):
    """Fail immediately with a useful step name if a Studionet tx fails."""
    assert tx_execution_succeeded(receipt), f"Studionet transaction failed: {step}"
    print(f"[PASS] {step}")


def test_quizambig_full_lifecycle_on_studionet(
    default_account,
    accounts,
):
    """Deploy Quizambig and execute one real quiz/evaluation lifecycle."""

    assert len(accounts) >= 2, (
        "Studionet test requires at least two configured accounts"
    )

    master = default_account
    player = accounts[1]

    print("\n===== QUIZAMBIG STUDIONET LIVE TEST =====")
    print("DEPLOYER / MASTER:", master.address)
    print("PLAYER:", player.address)

    # get_contract_factory resolves this path relative to the configured
    # contracts directory, so do not use "contracts/quizambig.py" here.
    factory = get_contract_factory(contract_file_path="quizambig.py")

    # Real deployment to the selected GenLayer network.
    contract = factory.deploy(
        account=master,
        consensus_max_rotations=5,
    )

    print("DEPLOYED CONTRACT:", contract.address)

    master_view = contract
    player_contract = contract.connect(player)

    answer = "4"
    salt = "quizambig-studionet-live-2026"
    answer_mode = "NUMERIC"
    commitment = make_commitment(answer, salt, answer_mode)

    # Writes return receipts, not the contract method's Python return value.
    # Capture the IDs from the authoritative next-ID views first.
    quiz_id = master_view.get_next_quiz_id().call()

    create_receipt = master_view.create_quiz(
        args=[
            "Studionet Semantic Evaluation",
            "Live GenLayer integration test",
            1,
            300,
        ]
    ).transact(
        consensus_max_rotations=5,
        wait_interval=3000,
        wait_retries=100,
    )
    assert_success(create_receipt, "create_quiz")

    assert master_view.get_next_quiz_id().call() == quiz_id + 1
    print("QUIZ ID:", quiz_id)

    question_id = master_view.get_next_question_id().call()

    add_question_receipt = master_view.add_question(
        args=[
            quiz_id,
            "What is 2 + 2?",
            commitment,
            len(answer),
            answer_mode,
            "The answer must express the numeric value four.",
            30,
            True,
        ]
    ).transact(
        consensus_max_rotations=5,
        wait_interval=3000,
        wait_retries=100,
    )
    assert_success(add_question_receipt, "add_question")

    assert master_view.get_next_question_id().call() == question_id + 1
    print("QUESTION ID:", question_id)

    publish_receipt = master_view.publish_quiz(
        args=[quiz_id]
    ).transact(
        consensus_max_rotations=5,
        wait_interval=3000,
        wait_retries=100,
    )
    assert_success(publish_receipt, "publish_quiz")

    join_receipt = player_contract.join_quiz(
        args=[quiz_id]
    ).transact(
        consensus_max_rotations=5,
        wait_interval=3000,
        wait_retries=100,
    )
    assert_success(join_receipt, "join_quiz")

    start_receipt = master_view.start_question(
        args=[question_id]
    ).transact(
        consensus_max_rotations=5,
        wait_interval=3000,
        wait_retries=100,
    )
    assert_success(start_receipt, "start_question")

    submit_receipt = player_contract.submit_answer(
        args=[question_id, "four"]
    ).transact(
        consensus_max_rotations=5,
        wait_interval=3000,
        wait_retries=100,
    )
    assert_success(submit_receipt, "submit_answer")

    # The contract's close_question rule is authoritative. The 30-second
    # custom deadline is intentionally long enough for Studionet RPC latency.
    # We wait only after the player's submission has been accepted.
    print("Waiting for the authoritative 30-second question deadline...")
    time.sleep(31)

    close_receipt = master_view.close_question(
        args=[question_id]
    ).transact(
        consensus_max_rotations=5,
        wait_interval=3000,
        wait_retries=100,
    )
    assert_success(close_receipt, "close_question")

    reveal_receipt = master_view.reveal_master_answer(
        args=[question_id, answer, salt]
    ).transact(
        consensus_max_rotations=5,
        wait_interval=3000,
        wait_retries=100,
    )
    assert_success(reveal_receipt, "reveal_master_answer")

    print("Starting REAL GenLayer nondeterministic semantic evaluation...")

    # This is the actual Phase 3 GenLayer nondeterministic evaluation.
    # The contract performs leader/validator consensus internally.
    evaluate_receipt = master_view.evaluate_submission(
        args=[question_id, player]
    ).transact(
        consensus_max_rotations=5,
        wait_interval=3000,
        wait_retries=200,
    )
    assert_success(evaluate_receipt, "evaluate_submission")

    evaluation = master_view.get_evaluation(
        args=[question_id, player]
    ).call()

    print("EVALUATION:", evaluation)

    assert evaluation["evaluation_status"] == "FINALIZED"
    assert isinstance(evaluation["semantic_score"], int)
    assert 0 <= evaluation["semantic_score"] <= 100
    assert evaluation["evaluation_correct"] is True

    print("[PASS] FINALIZED semantic evaluation")
    print("===== QUIZAMBIG STUDIONET TEST COMPLETE =====\n")
