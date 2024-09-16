from ..base_agent import Agent
from typing import Dict, Any
from ...prompts.refine_prompts import get_prompt
from ...output import Gen
import random


class RefineAgent(Agent):
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        refine_prompt = get_prompt("refine_system_prompt")
        refine_user_prompt = get_prompt(
            "refine_user_prompt",
            question=input_data['question'],
            correct_answer=input_data['correct_answer'],
            distractions=input_data['distractors'],
            evaluation=input_data['eval_responses'],
        )

        reply = self._get_reply(input_data['image_path'], refine_prompt, refine_user_prompt, Gen)
        distractors = reply.parsed.distractors
        options = distractors + [input_data['correct_answer']]
        random.shuffle(options)
        return {'options': options, 'distractors': distractors}