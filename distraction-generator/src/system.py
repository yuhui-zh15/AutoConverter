import random
from typing import List, Tuple

from loguru import logger

from .agents.evaluation.evaluation_agent import EvaluationAgent
from .agents.generation.main_distractor_agent import MainDistractorAgent
from .agents.refine.refine_agent import RefineAgent
from .agents.student.student_response_fusion_agent import StudentResponseFusionAgent

# logging.basicConfig(level=logging.INFO)
# logging.getLogger(__name__)


class DistractionGeneratorSystem:
    def __init__(
        self,
        image_path: str,
        question: str,
        correct_answer: str,
        model: str,
        api_key: str,
        max_rounds: int = 4,
        initial_distractor_count: int = 9,
    ):
        self.image_path = image_path
        self.question = question
        self.correct_answer = correct_answer
        self.max_rounds = max_rounds
        self.initial_distractor_count = initial_distractor_count

        self.agents = [
            MainDistractorAgent(model, api_key),
            StudentResponseFusionAgent(model, api_key),
            EvaluationAgent(model, api_key),
            RefineAgent(model, api_key),
        ]

    def generate_distractions(self) -> str:
        # logger.info(f"Question: {self.question}")
        # logger.info(f"Correct Answer: {self.correct_answer}")

        input_data = {
            "image_path": self.image_path,
            "question": self.question,
            "correct_answer": self.correct_answer,
        }

        round_num = 0
        while round_num < self.max_rounds:
            try:
                if round_num == 0:
                    input_data.update(self.agents[0].process(input_data))
                else:
                    for agent in self.agents[1:]:
                        input_data.update(agent.process(input_data))

                self._validate_distractors(input_data["distractors"], round_num)
                # self._print_options(round_num, input_data["options"])

                if round_num == self.max_rounds - 1:
                    return self._format_question(input_data["distractors"])

                round_num += 1

            except ValueError as e:
                logger.error(f"Error in round {round_num}: {e}")
                logger.info("Restarting the generation process from round 0")
                round_num = 0
                input_data = {
                    "image_path": self.image_path,
                    "question": self.question,
                    "correct_answer": self.correct_answer,
                }

    def _validate_distractors(self, distractors: List[str], round_num: int):
        expected_count = self.initial_distractor_count - 2 * round_num
        if len(distractors) != expected_count:
            raise ValueError(
                f"Unexpected number of distractors. Expected {expected_count}, got {len(distractors)}."
            )

    # @staticmethod
    # def _print_options(round_num: int, options: List[str]):
    #     logger.info(f"Round {round_num}:")
    #     for i, option in enumerate(options):
    #         logger.info(f"{i}. {option}")
    #     logger.info("--------------------------------")

    def _format_question(self, distractors: List[str]) -> Tuple[str, str]:
        if len(distractors) > 3:
            distractors = random.sample(distractors, 3)
        elif len(distractors) < 3:
            logger.error(
                "Not enough options generated. Filling with placeholder options."
            )
        multiple_choice = distractors + [self.correct_answer]
        random.shuffle(multiple_choice)
        correct_index = multiple_choice.index(self.correct_answer)
        correct_letter = chr(65 + correct_index)

        formatted_question = f"Question: {self.question}\n"
        formatted_question += "\n".join(
            f"{chr(65 + i)}. {option}" for i, option in enumerate(multiple_choice)
        )
        answer = correct_letter

        return formatted_question, answer
