# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import hashlib
from datetime import datetime, timezone


class Quizambig(gl.Contract):
    """
    Quizambig phase 2.

    Phase 2 adds player registration, authoritative question timing,
    one-submission-per-player enforcement, question closure, and a
    cryptographic master-answer commitment/reveal flow.

    GenLayer semantic evaluation is intentionally the next phase.
    """

    next_quiz_id: u32
    next_question_id: u32

    quiz_master: TreeMap[str, Address]
    quiz_title: TreeMap[str, str]
    quiz_description: TreeMap[str, str]
    quiz_question_count: TreeMap[str, u32]
    quiz_overall_duration: TreeMap[str, u64]
    quiz_created_at: TreeMap[str, u64]
    quiz_published_at: TreeMap[str, u64]
    quiz_status: TreeMap[str, str]

    question_quiz_id: TreeMap[str, str>
    question_text: TreeMap[str, str]
    question_answer_commitment: TreeMap[str, str]
    question_answer_length: TreeMap[str, u32>
    question_criteria: TreeMap[str, str]
    question_automatic_time: TreeMap[str, u32>
    question_custom_time: TreeMap[str, u32>
    question_has_custom_time: TreeMap[str, bool]
    question_final_time: TreeMap[str, u32>
    question_start_time: TreeMap[str, u64>
    question_deadline: TreeMap[str, u64>
    question_status: TreeMap[str, str]
    question_revealed_answer: TreeMap[str, str]
    question_revealed: TreeMap[str, bool]

    player_joined: TreeMap[str, bool]
    submission_exists: TreeMap[str, bool]
    submission_answer: TreeMap[str, str>
    submission_time: TreeMap[str, u64>
    submission_response_time: TreeMap[str, u64>

    def __init__(self):
        self.next_quiz_id = 1
        self.next_question_id = 1

    def _now(self) -> u64:
        return u64(int(datetime.now(timezone.utc).timestamp()))

    def _quiz_key(self, quiz_id: u32) -> str:
        return str(quiz_id)

    def _question_key(self, question_id: u32) -> str:
        return str(question_id)

    def _player_key(self, quiz_id: u32, player: Address) -> str:
        return str(quiz_id) + ":" + player.as_hex

    def _submission_key(self, question_id: u32, player: Address) -> str:
        return str(question_id) + ":" + player.as_hex

    def _require_quiz_master(self, quiz_id: u32):
        key = self._quiz_key(quiz_id)
        assert self.quiz_master[key] == gl.message.sender_address, "only the Quiz Master can modify this quiz"

    def _require_quiz_exists(self, quiz_id: u32):
        key = self._quiz_key(quiz_id)
        assert self.quiz_master[key] != Address("0x0000000000000000000000000000000000000000"), "quiz does not exist"

    def _require_question_exists(self, question_id: u32):
        key = self._question_key(question_id)
        assert self.question_quiz_id[key] != "", "question does not exist"

    def _quiz_expiry(self, quiz_id: u32) -> u64:
        quiz_key = self._quiz_key(quiz_id)
        return self.quiz_published_at[quiz_key] + self.quiz_overall_duration[quiz_key]

    def _answer_commitment(self, answer: str, salt: str) -> str:
        payload = (answer + ":" + salt).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @gl.public.view
    def get_next_quiz_id(self) -> int:
        return self.next_quiz_id

    @gl.public.view
    def get_next_question_id(self) -> int:
        return self.next_question_id

    @gl.public.view
    def get_quiz(self, quiz_id: u32) -> dict:
        self._require_quiz_exists(quiz_id)
        key = self._quiz_key(quiz_id)
        return {
            "id": quiz_id,
            "master": self.quiz_master[key].as_hex,
            "title": self.quiz_title[key],
            "description": self.quiz_description[key],
            "question_count": self.quiz_question_count[key],
            "overall_duration_seconds": self.quiz_overall_duration[key],
            "created_at": self.quiz_created_at[key],
            "published_at": self.quiz_published_at[key],
            "expires_at": self._quiz_expiry(quiz_id),
            "status": self.quiz_status[key],
        }

    @gl.public.view
    def get_question(self, question_id: u32) -> dict:
        self._require_question_exists(question_id)
        key = self._question_key(question_id)
        return {
            "id": question_id,
            "quiz_id": self.question_quiz_id[key],
            "question_text": self.question_text[key],
            "answer_length": self.question_answer_length[key],
            "automatic_time": self.question_automatic_time[key],
            "custom_time": self.question_custom_time[key],
            "has_custom_time": self.question_has_custom_time[key],
            "final_time": self.question_final_time[key],
            "start_time": self.question_start_time[key],
            "deadline": self.question_deadline[key],
            "status": self.question_status[key],
            "answer_revealed": self.question_revealed[key],
        }

    @gl.public.view
    def get_player_status(self, quiz_id: u32, player: Address) -> dict:
        self._require_quiz_exists(quiz_id)
        return {
            "joined": self.player_joined[self._player_key(quiz_id, player)],
            "quiz_id": quiz_id,
            "player": player.as_hex,
        }

    @gl.public.view
    def get_submission(self, question_id: u32, player: Address) -> dict:
        self._require_question_exists(question_id)
        key = self._submission_key(question_id, player)
        assert self.submission_exists[key], "submission does not exist"
        return {
            "question_id": question_id,
            "player": player.as_hex,
            "answer": self.submission_answer[key],
            "submitted_at": self.submission_time[key],
            "response_time_seconds": self.submission_response_time[key],
        }

    @gl.public.view
    def get_revealed_answer(self, question_id: u32) -> str:
        self._require_question_exists(question_id)
        key = self._question_key(question_id)
        assert self.question_revealed[key], "master answer has not been revealed"
        return self.question_revealed_answer[key]

    @gl.public.write
    def create_quiz(
        self,
        title: str,
        description: str,
        question_count: u32,
        overall_duration_seconds: u64,
    ) -> int:
        assert question_count > 0, "question_count must be greater than zero"
        assert overall_duration_seconds > 0, "overall duration must be greater than zero"

        quiz_id = self.next_quiz_id
        self.next_quiz_id += 1

        key = self._quiz_key(quiz_id)
        self.quiz_master[key] = gl.message.sender_address
        self.quiz_title[key] = title
        self.quiz_description[key] = description
        self.quiz_question_count[key] = question_count
        self.quiz_overall_duration[key] = overall_duration_seconds
        self.quiz_created_at[key] = self._now()
        self.quiz_published_at[key] = 0
        self.quiz_status[key] = "DRAFT"

        return quiz_id

    @gl.public.write
    def add_question(
        self,
        quiz_id: u32,
        question_text: str,
        answer_commitment: str,
        answer_length: u32,
        evaluation_criteria: str,
        custom_time_seconds: u32,
        use_custom_time: bool,
    ) -> int:
        self._require_quiz_master(quiz_id)

        quiz_key = self._quiz_key(quiz_id)
        assert self.quiz_status[quiz_key] == "DRAFT", "questions can only be added to a draft"
        assert self.question_text_count_for_quiz(quiz_id) < self.quiz_question_count[quiz_key], "question limit reached"
        assert question_text != "", "question text is required"
        assert len(answer_commitment) == 64, "answer commitment must be a SHA-256 hex digest"
        assert answer_length > 0, "answer length must be greater than zero"
        assert evaluation_criteria != "", "evaluation criteria is required"

        automatic_time = answer_length

        if use_custom_time:
            assert custom_time_seconds > 0, "custom question time must be greater than zero"
            final_time = custom_time_seconds
        else:
            final_time = automatic_time

        question_id = self.next_question_id
        self.next_question_id += 1
        key = self._question_key(question_id)

        self.question_quiz_id[key] = quiz_key
        self.question_text[key] = question_text
        self.question_answer_commitment[key] = answer_commitment.lower()
        self.question_answer_length[key] = answer_length
        self.question_criteria[key] = evaluation_criteria
        self.question_automatic_time[key] = automatic_time
        self.question_custom_time[key] = custom_time_seconds
        self.question_has_custom_time[key] = use_custom_time
        self.question_final_time[key] = final_time
        self.question_start_time[key] = 0
        self.question_deadline[key] = 0
        self.question_status[key] = "CREATED"
        self.question_revealed_answer[key] = ""
        self.question_revealed[key] = False

        return question_id

    @gl.public.view
    def question_text_count_for_quiz(self, quiz_id: u32) -> int:
        quiz_key = self._quiz_key(quiz_id)
        count = 0
        for question_id in range(1, self.next_question_id):
            key = self._question_key(question_id)
            if self.question_quiz_id[key] == quiz_key:
                count += 1
        return count

    @gl.public.write
    def publish_quiz(self, quiz_id: u32) -> None:
        self._require_quiz_master(quiz_id)

        quiz_key = self._quiz_key(quiz_id)
        assert self.quiz_status[quiz_key] == "DRAFT", "quiz is not a draft"
        assert self.question_text_count_for_quiz(quiz_id) == self.quiz_question_count[quiz_key], "all questions must be added before publishing"

        self.quiz_status[quiz_key] = "PUBLISHED"
        self.quiz_published_at[quiz_key] = self._now()

        for question_id in range(1, self.next_question_id):
            key = self._question_key(question_id)
            if self.question_quiz_id[key] == quiz_key:
                self.question_status[key] = "PUBLISHED"

    @gl.public.write
    def join_quiz(self, quiz_id: u32) -> None:
        self._require_quiz_exists(quiz_id)

        quiz_key = self._quiz_key(quiz_id)
        player_key = self._player_key(quiz_id, gl.message.sender_address)

        assert self.quiz_status[quiz_key] == "PUBLISHED", "quiz is not open for joining"
        assert self._now() < self._quiz_expiry(quiz_id), "quiz joining period has expired"
        assert not self.player_joined[player_key], "player has already joined"

        self.player_joined[player_key] = True
        self.quiz_status[quiz_key] = "ACTIVE"

    @gl.public.write
    def start_question(self, question_id: u32) -> None:
        self._require_question_exists(question_id)

        question_key = self._question_key(question_id)
        quiz_id = u32(int(self.question_quiz_id[question_key]))
        self._require_quiz_master(quiz_id)

        quiz_key = self._quiz_key(quiz_id)
        assert self.quiz_status[quiz_key] == "ACTIVE", "quiz is not active"
        assert self._now() < self._quiz_expiry(quiz_id), "overall quiz duration has expired"
        assert self.question_status[question_key] == "PUBLISHED", "question is not ready to start"

        start = self._now()
        deadline = start + self.question_final_time[question_key]
        quiz_expiry = self._quiz_expiry(quiz_id)
        if deadline > quiz_expiry:
            deadline = quiz_expiry

        self.question_start_time[question_key] = start
        self.question_deadline[question_key] = deadline
        self.question_status[question_key] = "ACTIVE"

    @gl.public.write
    def submit_answer(self, question_id: u32, answer: str) -> None:
        self._require_question_exists(question_id)

        question_key = self._question_key(question_id)
        quiz_id = u32(int(self.question_quiz_id[question_key]))
        quiz_key = self._quiz_key(quiz_id)
        player_key = self._player_key(quiz_id, gl.message.sender_address)
        submission_key = self._submission_key(question_id, gl.message.sender_address)

        assert self.player_joined[player_key], "player has not joined this quiz"
        assert self.quiz_status[quiz_key] == "ACTIVE", "quiz is not active"
        assert self.question_status[question_key] == "ACTIVE", "question is not active"
        assert self._now() <= self.question_deadline[question_key], "question deadline has passed"
        assert not self.submission_exists[submission_key], "player already submitted an answer"

        submitted_at = self._now()
        response_time = submitted_at - self.question_start_time[question_key]

        self.submission_exists[submission_key] = True
        self.submission_answer[submission_key] = answer
        self.submission_time[submission_key] = submitted_at
        self.submission_response_time[submission_key] = response_time

    @gl.public.write
    def close_question(self, question_id: u32) -> None:
        self._require_question_exists(question_id)

        question_key = self._question_key(question_id)
        quiz_id = u32(int(self.question_quiz_id[question_key]))
        self._require_quiz_master(quiz_id)

        assert self.question_status[question_key] == "ACTIVE", "question is not active"
        assert self._now() >= self.question_deadline[question_key], "question is still within its deadline"

        self.question_status[question_key] = "CLOSED"

    @gl.public.write
    def reveal_master_answer(self, question_id: u32, answer: str, salt: str) -> None:
        self._require_question_exists(question_id)

        question_key = self._question_key(question_id)
        quiz_id = u32(int(self.question_quiz_id[question_key]))
        self._require_quiz_master(quiz_id)

        assert self.question_status[question_key] == "CLOSED", "question must be closed before reveal"
        assert not self.question_revealed[question_key], "master answer is already revealed"

        expected = self.question_answer_commitment[question_key]
        actual = self._answer_commitment(answer, salt)
        assert actual == expected, "master answer does not match commitment"

        self.question_revealed_answer[question_key] = answer
        self.question_revealed[question_key] = True
        self.question_status[question_key] = "ANSWER_REVEALED"
