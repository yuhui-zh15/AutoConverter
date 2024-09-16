from typing import Any, Dict

from ...output import Gen
from ...prompts.generate_prompts import get_prompt
from ..base_agent import Agent


class VisualInterpretationAgent(Agent):
    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        visual_prompt = get_prompt("visual_interpretation_generation_system_prompt")
        visual_user_prompt = get_prompt(
            "generation_user_prompt",
            question=input_data["question"],
            correct_answer=input_data["correct_answer"],
        )

        reply = self._get_reply(
            input_data["image_path"], visual_prompt, visual_user_prompt, Gen
        )
        distractors = reply.parsed.distractors

        return {"distractors": distractors}
