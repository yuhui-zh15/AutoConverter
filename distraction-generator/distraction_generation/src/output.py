from pydantic import BaseModel


class Gen(BaseModel):
    distractors: list[str]


class Test(BaseModel):
    class Option(BaseModel):
        option: str
        judgment: bool
        reasoning: str
        confidence: int

    options: list[Option]


class Eval(BaseModel):
    class Option(BaseModel):
        class Score(BaseModel):
            plausibility: int
            effectiveness: int
            distinctiveness: int
            clarity: int
            relevance: int
            difficulty: int
            average: float

        option: str
        score: Score
        explanation: str
        suggestion: str

    class Abandon(BaseModel):
        option1: str
        option2: str

    options: list[Option]
    abandon: Abandon
