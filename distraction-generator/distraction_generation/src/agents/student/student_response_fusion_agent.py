from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

from ..base_agent import Agent
from .high_achieving_agent import HighAchievingAgent
from .knowledge_deficient_agent import KnowledgeDeficientAgent
from .linguistically_sensitive_agent import LinguisticallySensitiveAgent
from .time_pressured_intuitive_agent import TimePressuredIntuitiveAgent
from .visually_sensitive_agent import VisuallySensitiveAgent


class StudentResponseFusionAgent(Agent):
    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        self.student_agents = {
            "high_achieving": HighAchievingAgent(model, api_key),
            "linguistically_sensitive": LinguisticallySensitiveAgent(model, api_key),
            "knowledge_deficient": KnowledgeDeficientAgent(model, api_key),
            "time_pressured_intuitive": TimePressuredIntuitiveAgent(model, api_key),
            "visually_sensitive": VisuallySensitiveAgent(model, api_key),
        }

    def _run_student_agents(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        with ThreadPoolExecutor(max_workers=len(self.student_agents)) as executor:
            future_to_agent = {
                executor.submit(agent.process, input_data): name
                for name, agent in self.student_agents.items()
            }
            all_responses = {}
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                result = future.result()
                all_responses[agent_name] = result
                # print(f"Response from {agent_name}: {result}")
        return all_responses

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        all_responses = self._run_student_agents(input_data)

        return {"test_responses": all_responses}
