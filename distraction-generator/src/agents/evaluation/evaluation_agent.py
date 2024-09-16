import json
from typing import Any, Dict

from ...output import Eval
from ...prompts.eval_prompts import get_prompt
from ..base_agent import Agent


class EvaluationAgent(Agent):
    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        eval_prompt = get_prompt("eval_system_prompt")
        eval_user_prompt = get_prompt(
            "eval_user_prompt",
            question=input_data["question"],
            correct_answer=input_data["correct_answer"],
            distractions=input_data["distractors"],
            test_responses=input_data["test_responses"],
        )

        reply = self._get_reply(
            input_data["image_path"], eval_prompt, eval_user_prompt, Eval
        )
        eval_result = reply.parsed.options
        abandon_options = reply.parsed.abandon

        eval_responses = json.dumps(
            [
                self._eval_to_dict(option)
                for option in eval_result
                if option.option
                not in [abandon_options.option1, abandon_options.option2]
            ],
            indent=2,
        )

        distractors = [
            option
            for option in input_data["distractors"]
            if option not in [abandon_options.option1, abandon_options.option2]
        ]
        print(distractors)

        options = [input_data["correct_answer"]] + distractors

        return {
            "eval_responses": eval_responses,
            "distractors": distractors,
            "options": options,
        }

    @staticmethod
    def _eval_to_dict(option):
        return {
            "option": option.option,
            "score": {
                "plausibility": option.score.plausibility,
                "effectiveness": option.score.effectiveness,
                "distinctiveness": option.score.distinctiveness,
                "clarity": option.score.clarity,
                "relevance": option.score.relevance,
                "difficulty": option.score.difficulty,
                "average": option.score.average,
            },
            "explanation": option.explanation,
            "suggestion": option.suggestion,
        }
