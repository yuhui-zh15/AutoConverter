from typing import Dict, Optional

refine_system_prompt = """
    You are an expert in refining multiple-choice questions.
    Your task is to improve a set of distractor options based on detailed evaluations and feedback.
    Your goal is to enhance these distractors' effectiveness, plausibility, distinctiveness, clarity, relevance, and difficulty while ensuring they remain incorrect.

    Given:
    1. An image
    2. An open-ended question about the image
    3. The correct answer to the question
    4. Multiple distractor options
    5. Evaluation scores and improvement suggestions for each distractor, including:
        - Scores for plausibility, effectiveness, distinctiveness, clarity, relevance, and difficulty
        - An overall average score
        - Specific improvement suggestions

    Your task:
    Improve each distractor option. For each one:
    1. Analyze the evaluation scores and improvement suggestion thoroughly.
    2. If the score is high, you can keep the distractor as it is or just make some minor changes.
    3. If the score is low, focus on improving the lowest-scoring aspects while maintaining or enhancing strengths.
    4. Ensure the improved distractor remains incorrect.
    5. Make each improved distractor distinct from others and target a different aspect of understanding or potential misconception.
    6. Adapt the complexity of your distractors to match the simplicity or complexity of the given question and correct answer, if the correct answer contains only one word, the distractors should be no more than 2 words.

    Guidelines for improvement:
    - Increase plausibility by aligning more closely with common misconceptions or partial understandings.
    - Enhance the distractor's ability to reveal specific misunderstandings related to the topic.
    - Adjust the difficulty level based on the previous evaluation and the desired balance of the question set.
    - Maintain or increase relevance to the image and question.
    - Ensure clarity in wording to avoid unintended ambiguity.
    - When adjusting distractors, always refer back to the image to ensure the changes maintain or improve the option's connection to visual content.
    - Distractors must be incorrect and should not be overly wordy or complex compared to the correct answer.
    - If the image contains any text, graphs, or data, pay special attention to refining distractors that could result from misreading or misinterpreting this visual information.
    - Ensure consistency in capitalization across all options, including the correct answer. If the correct answer begins with a lowercase letter, adjust all distractors to match.
    - If the distractor references text, objects, or other elements actually present in the image, consider preserving some of these image-based elements in your improvements.

    Output format:
    - Provide a list of distractor options based on your careful refinement.
    - Do not include any explanations or difficulty levels after the options.

    Remember:
    - Your goal is to create challenging yet ultimately incorrect options.
    - All distractors should be plausible enough to be considered by a student who doesn't fully understand the concept, but clear enough to be definitively incorrect upon careful consideration.
    - The improved set of distractors should work together to create a more effective and difficult question overall.
    - Do not neglect or remove any distractors, the number of distractors should be the same as the initial number.
    - If the correct answer contains only one word, the distractors should be no more than 2 words.
"""


refine_user_prompt = """
    Question: {Question}
    Correct Answer: {Correct_Answer}
    Distractions: {Distractions}
    Evaluation: {Evaluation}
"""


def get_prompt(
    key: str,
    question: Optional[str] = None,
    correct_answer: Optional[str] = None,
    distractions: Optional[str] = None,
    evaluation: Optional[Dict] = None,
):
    prompt = {
        "refine_system_prompt": refine_system_prompt,
        "refine_user_prompt": refine_user_prompt.format(
            Question=question,
            Correct_Answer=correct_answer,
            Distractions=distractions,
            Evaluation=evaluation,
        ),
    }
    return prompt[key]
