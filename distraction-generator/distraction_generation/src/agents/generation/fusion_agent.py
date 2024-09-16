from typing import Any, Dict

from ...output import Gen
from ...prompts.generate_prompts import get_prompt
from ..base_agent import Agent


class FusionAgent(Agent):
    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        fusion_prompt = get_prompt("fusion_generation_system_prompt")
        fusion_user_prompt = get_prompt(
            "fusion_generation_user_prompt",
            question=input_data["question"],
            correct_answer=input_data["correct_answer"],
            all_distractors=input_data["all_distractors"],
        )

        reply = self._get_reply(
            input_data["image_path"], fusion_prompt, fusion_user_prompt, Gen
        )
        selected_distractors = reply.parsed.distractors

        return {"distractors": selected_distractors}
