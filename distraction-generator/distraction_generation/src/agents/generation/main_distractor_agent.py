import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from .concept_agent import ConceptAgent
from .data_processing_agent import DataProcessingAgent
from .fusion_agent import FusionAgent
from .reasoning_agent import ReasoningAgent
from .visual_interpretation_agent import VisualInterpretationAgent


class MainDistractorAgent:
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.generation_agents = {
            "concept error": ConceptAgent(model, api_key),
            "reasoning error": ReasoningAgent(model, api_key),
            "visual interpretation error": VisualInterpretationAgent(model, api_key),
            "data processing error": DataProcessingAgent(model, api_key),
        }
        self.fusion_agent = FusionAgent(model, api_key)

    def _run_generation_agents(
        self, input_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        with ThreadPoolExecutor(max_workers=len(self.generation_agents)) as executor:
            future_to_agent = {
                executor.submit(agent.process, input_data): name
                for name, agent in self.generation_agents.items()
            }
            all_distractors = {}
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                result = future.result()
                all_distractors[agent_name] = result["distractors"]
                # print(f"Distractors from {agent_name}: {result['distractors']}")
        return all_distractors

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        all_distractors = self._run_generation_agents(input_data)
        # print(f"All distractors: {all_distractors}")

        fusion_input = input_data.copy()
        fusion_input["all_distractors"] = all_distractors

        fusion_result = self.fusion_agent.process(fusion_input)
        selected_distractors = fusion_result["distractors"]

        options = selected_distractors + [input_data["correct_answer"]]
        random.shuffle(options)

        return {"options": options, "distractors": selected_distractors}
