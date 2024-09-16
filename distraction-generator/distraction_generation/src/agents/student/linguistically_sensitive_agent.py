import json
from typing import Any, Dict

from ...output import Test
from ...prompts.test_prompts import get_prompt
from ..base_agent import Agent


class LinguisticallySensitiveAgent(Agent):
    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        test_prompt = get_prompt("linguistically_sensitive_system_prompt")
        test_user_prompt = get_prompt(
            "test_user_prompt",
            question=input_data["question"],
            options=input_data["options"],
        )

        reply = self._get_reply(
            input_data["image_path"], test_prompt, test_user_prompt, Test
        )
        linguistically_sensitive_responses = json.dumps(
            [self._test_to_dict(option) for option in reply.parsed.options], indent=2
        )

        return {
            "linguistically_sensitive_responses": linguistically_sensitive_responses
        }

    @staticmethod
    def _test_to_dict(option):
        return {
            "option": option.option,
            "judgment": option.judgment,
            "reasoning": option.reasoning,
            "confidence": option.confidence,
        }
