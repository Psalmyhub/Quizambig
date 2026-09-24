# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


class Quizambig(gl.Contract):
    """Initial Quizambig contract skeleton.

    This first milestone deliberately keeps the state model small. The
    production contract will add protected answer commitments, submissions,
    semantic evaluation results, scoring, and leaderboard state in tested
    increments.
    """

    owner: Address
    next_quiz_id: u32

    def __init__(self):
        self.owner = gl.message.sender_address
        self.next_quiz_id = 1

    @gl.public.view
    def get_owner(self) -> str:
        return self.owner.as_hex

    @gl.public.view
    def get_next_quiz_id(self) -> int:
        return self.next_quiz_id

    @gl.public.write
    def create_quiz(
        self,
        title: str,
        description: str,
        question_count: u32,
        overall_duration_seconds: u32,
    ) -> int:
        assert self.owner == gl.message.sender_address, "only owner can create prototype quizzes"
        assert question_count > 0, "question_count must be greater than zero"
        assert overall_duration_seconds > 0, "overall duration must be greater than zero"

        quiz_id = self.next_quiz_id
        self.next_quiz_id += 1
        return quiz_id
