import abc
from typing import Dict, Any
from ..get_reply import get_reply

class Agent(abc.ABC):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    @abc.abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def _get_reply(self, image_path: str, system_prompt: str, user_prompt: str, format_class):
        return get_reply(
            image_path=image_path,
            model=self.model,
            api_key=self.api_key,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            format=format_class,
        )