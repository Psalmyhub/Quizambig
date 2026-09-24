# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from datetime import datetime, timezone


class Quizambig(gl.Contract):
    """
    Quizambig phase 1 contract.

    This phase establishes the deterministic quiz/question lifecycle and timing
    model. Semantic GenLayer evaluation and cryptographic answer reveal are
    added only after this state model is tested.
    """

    next_quiz_id: u32
    next_question_id: u32

    quiz_master: TreeMap[str, Address]
    quiz_title: TreeMap[str, str]
    quiz_description: TreeMap[str, str]
    quiz_question_count: TreeMap[str, u32]
    quiz_overall_duration: TreeMap[str, u64>
    quiz_created_at: TreeMap[str, u64>
    quiz_published_at: TreeMap[str, u64>
    quiz_status: TreeMap[str, str>

    question_quiz_id: TreeMap[str, str>
    question_text: TreeMap[str, str>
    question_answer_commitment: TreeMap[str, bytes>
    question_answer_length: TreeMap[str, u32>
    question_criteria: TreeMap[str, str>
    question_automatic_time: TreeMap[str, u32>
    question_custom_time: TreeMap[str, u32>
    question_has_custom_time: TreeMap[str, bool>
    question_final_time: TreeMap[str, u32>
    question_status: TreeMap[str, str>

    def __init__(self):
        self.next_quiz_id = 1
        self.next_question_id = 1

    def _now(self) -> u64:
        return u64(int(datetime.now(timezone.utc).timestamp()))

    def _quiz_key(self, quiz_id: u32) -> str:
        return str(quiz_id)

    def _question_key(self, question_id: u32) -> str:
        return str(question_id)

    def _require_quiz_master(self, quiz_id: u32):
        key = self._quiz_key(quiz_id)
        assert self.quiz_master[key] == gl.message.sender_address, "only the Quiz Master can modify this quiz"

    @gl.public.view
    def get_next_quiz_id(self) -> int:
        return self.next_quiz_id

    @gl.public.view
    def get_next_question_id(self) -> int:
        return self.next_question_id

    @gl.public.view
    def get_quiz(self, quiz_id: u32) -> dict:
        key = self._quiz_key(quiz_id)
        assert self.quiz_master[key] != Address("0x0000000000000000000000000000000000000000"), "quiz does not exist"
        return {
            "id": quiz_id,
            "master": self.quiz_master[key].as_hex,
            "title": self.quiz_title[key],
            "description": self.quiz_description[key],
            "question_count": self.quiz_question_count[key],
            "overall_duration_seconds": self.quiz_overall_duration[key],
            "created_at": self.quiz_created_at[key],
            "published_at": self.quiz_published_at[key],
            "status": self.quiz_status[key],
        }

    @gl.public.view
    def get_question(self, question_id: u32) -> dict:
        key = self._question_key(question_id)
        assert self.question_quiz_id[key] != "", "question does not exist"
        return {
            "id": question_id,
            "quiz_id": self.question_quiz_id[key],
            "question_text": self.question_text[key],
            "answer_length": self.question_answer_length[key],
            "automatic_time": self.question_automatic_time[key],
            "custom_time": self.question_custom_time[key],
            "has_custom_time": self.question_has_custom_time[key],
            "final_time": self.question_final_time[key],
            "criteria": self.question_criteria[key],
            "status": self.question_status[key],
        }

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
        answer_commitment: bytes,
        answer_length: u32,
        evaluation_criteria: str,
        custom_time_seconds: u32,
        use_custom_time: bool,
    ) -> int:
        self._require_quiz_master(quiz_id)

        quiz_key = self._quiz_key(quiz_id)
        assert self.quiz_status[quiz_key] == "DRAFT", "questions can only be added to a draft"
        assert self.quiz_question_count[quiz_key] > 0, "invalid quiz"
        assert self.question_text_count_for_quiz(quiz_id) < self.quiz_question_count[quiz_key], "question limit reached"
        assert question_text != "", "question text is required"
        assert len(answer_commitment) > 0, "answer commitment is required"
        assert answer_length > 0, "answer length must be greater than zero"
        assert evaluation_criteria != "", "evaluation criteria is required"

        # Phase-1 automatic timing is deliberately simple: one second per
        # character of the master answer. The production timing formula will
        # be finalized and separately tested before launch.
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
        self.question_answer_commitment[key] = answer_commitment
        self.question_answer_length[key] = answer_length
        self.question_criteria[key] = evaluation_criteria
        self.question_automatic_time[key] = automatic_time
        self.question_custom_time[key] = custom_time_seconds
        self.question_has_custom_time[key] = use_custom_time
        self.question_final_time[key] = final_time
        self.question_status[key] = "CREATED"

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
