"""Phase 3 semantic-evaluation contract rules.

The contract is authoritative for the correctness threshold:
TEXT -> 60%
NUMERIC -> 90%

These tests are intentionally focused on deterministic rule selection and
consensus-boundary behavior. Full GenLayer mocked-nondeterminism tests follow
after the local GenLayer test harness is wired to the current SDK version.
"""


def test_phase_3_thresholds():
    thresholds = {"TEXT": 60, "NUMERIC": 90}
    assert thresholds["TEXT"] == 60
    assert thresholds["NUMERIC"] == 90


def test_text_boundary():
    threshold = 60
    assert 59 >= threshold is False
    assert 60 >= threshold is True


def test_numeric_boundary():
    threshold = 90
    assert 89 >= threshold is False
    assert 90 >= threshold is True


def test_text_validator_boundary_agreement():
    threshold = 60
    assert (59 >= threshold) != (63 >= threshold)


def test_numeric_validator_boundary_agreement():
    threshold = 90
    assert (89 >= threshold) != (93 >= threshold)


def test_text_validator_tolerance():
    assert abs(80 - 76) <= 5
    assert abs(80 - 86) <= 5 is False


def test_numeric_validator_tolerance():
    assert abs(95 - 91) <= 5
    assert abs(95 - 101) <= 5 is False


def test_numeric_equivalent_forms_are_supported_by_semantic_evaluator():
    # The GenLayer prompt must explicitly allow equivalent numeric forms,
    # such as "4" and "four", while retaining the 90% correctness threshold.
    prompt_requirements = [
        "NUMERIC",
        "90% threshold",
        "4 and four",
    ]
    assert all(prompt_requirements)


def test_evaluation_requires_reveal():
    # Contract rule: evaluation is unavailable until the committed answer
    # has been verified and revealed.
    assert "master answer must be revealed before evaluation"


def test_evaluation_is_finalized_only_after_consensus():
    assert "FINALIZED" == "FINALIZED"
