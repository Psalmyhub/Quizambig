"""Live Quizambig integration test.

Run explicitly on GenLayer Studionet:

    gltest --network studionet tests/test_quizambig_studionet.py -v -s
"""

import hashlib
import time

from gltest.contracts.contract_factory import get_contract_factory


def make_commitment(answer: str, salt: str, answer_mode: str) -> str:
    payload = f"{answer}:{salt}:{answer_mode}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_quizambig_full_lifecycle_on_studionet(
    default_account,
    accounts,
):
    """Deploy Quizambig and execute one real quiz/evaluation lifecycle."""

    assert len(accounts) >= 2, "Studionet test requires at least two configured accounts"

    master = default_account
    player = accounts[1]

    factory = get_contract_factory(contract_file_path="contracts/quizambig.py")
    contract = factory.deploy(account=master)

    master_view = contract
    player_contract = contract.connect(player)

    answer = "4"
    salt = "quizambig-studionet-live-2026"
    answer_mode = "NUMERIC"
    commitment = make_commitment(answer, salt, answer_mode)

    quiz_id = master_view.create_quiz(
        "Studionet Semantic Evaluation",
        "Live GenLayer integration test",
        1,
        300,
    ).transact()

    question_id = master_view.add_question(
        quiz_id,
        "What is 2 + 2?",
        commitment,
        len(answer),
        answer_mode,
        "The answer must express the numeric value four.",
        3,
        True,
    ).transact()

    master_view.publish_quiz(quiz_id).transact()

    player_contract.join_quiz(quiz_id).transact()

    master_view.start_question(question_id).transact()

    player_contract.submit_answer(question_id, "four").transact()

    # The contract's close_question rule is authoritative. This sleep only
    # lets the 3-second question deadline elapse before the close transaction.
    time.sleep(4)

    master_view.close_question(question_id).transact()

    master_view.reveal_master_answer(
        question_id,
        answer,
        salt,
    ).transact()

    # This is the actual GenLayer nondeterministic semantic evaluation.
    master_view.evaluate_submission(question_id, player).transact()

    evaluation = master_view.get_evaluation(question_id, player).call()

    assert evaluation["evaluation_status"] == "FINALIZED"
    assert isinstance(evaluation["semantic_score"], int)
    assert 0 <= evaluation["semantic_score"] <= 100
    assert evaluation["evaluation_correct"] is True
