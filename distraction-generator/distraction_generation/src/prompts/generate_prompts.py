from typing import List, Optional

concept_generation_system_prompt = """
    You are an expert in creating challenging and educational multiple-choice questions, specializing in conceptual errors. 
    Your task is to generate plausible but incorrect options (distractions) for a given image-based question, focusing on conceptual misunderstandings and misconceptions.

    Given:
    1. An image
    2. An open-ended question about the image
    3. The correct answer to the question

    Your task:
    1. Carefully analyze and understand the image. Briefly describe the image content (for your understanding only, do not output this).
    2. Generate 9 unique and plausible distraction options based on conceptual errors. Each distraction should:
        - Be related to the image and question
        - Seem potentially correct at first glance
        - Be very misleading for students due to conceptual misunderstandings
        - Contain a subtle flaw or misconception that makes it incorrect
        - Vary in difficulty and the type of conceptual error it represents

    3. Ensure you understand the connection between the image, question, and the underlying concepts.
    4. Focus on common conceptual misconceptions in the subject area, including:
        - Concept Confusion: Create options that are similar to the correct concept but with subtle differences
        - Partial Correctness: Include options that contain partially correct information but are incomplete or misleading
        - Overgeneralization: Develop options that incorrectly apply specific cases to general situations

    5. Aim for a diverse set of distractors that test different aspects of conceptual understanding.
    6. Include 3 easy-level, 3 medium-level, and 3 difficult-level distractors among the 9 options, all focusing on conceptual errors.
    7. Each distractor should have some relation to the correct answer, but ensure they are distinctly different and incorrect due to conceptual misunderstandings.
    8. If the question involves a specific subject area, consider common conceptual difficulties unique to that field.
    9. Adapt the complexity of your distractors to match the simplicity or complexity of the given question and correct answer.

    Output format:
    - Provide a list of 9 distractor options based on conceptual errors.
    - Do not include any explanations or difficulty levels after the options.

    Remember:
    - Your goal is to create challenging yet ultimately incorrect options that specifically target conceptual misunderstandings.
    - All distractors should be plausible enough to be considered by a student who doesn't fully grasp the concept, but clear enough to be definitively incorrect upon careful consideration.
    - Focus exclusively on conceptual errors rather than other types of mistakes (e.g., calculation errors, visual misinterpretations). 
    - Distractors must be incorrect and should not be overly wordy or complex compared to the correct answer.
    - Ensure consistency in capitalization across all options, including the correct answer. If the correct answer begins with a lowercase letter, adjust all distractors to match.
"""

reasoning_generation_system_prompt = """
    You are an expert in creating challenging and educational multiple-choice questions, specializing in reasoning errors.
    Your task is to generate plausible but incorrect options (distractions) for a given image-based question, focusing on flaws in logical reasoning and inference.

    Given:
    1. An image
    2. An open-ended question about the image
    3. The correct answer to the question

    Your task:
    1. Carefully analyze and understand the image. Briefly describe the image content (for your understanding only, do not output this).
    2. Generate 9 unique and plausible distraction options based on reasoning errors. Each distraction should:
        - Be related to the image and question
        - Seem potentially correct at first glance
        - Be very misleading for students due to faulty reasoning
        - Contain a subtle logical flaw that makes it incorrect
        - Vary in difficulty and the type of reasoning error it represents

    3. Ensure you understand the logical steps required to correctly answer the question based on the image.
    4. Focus on common reasoning errors, including:
        - Complex Reasoning Flaws: Create options that require multi-step reasoning but contain logical gaps or invalid assumptions
        - Causal Inversion: Develop options that reverse cause and effect relationships
        - Context Neglect: Include options that ignore important contextual information provided in the question or image
        - False Analogies: Generate options that draw incorrect parallels or comparisons
        - Hasty Generalizations: Create options that jump to conclusions based on insufficient evidence

    5. Aim for a diverse set of distractors that test different aspects of logical reasoning and critical thinking.
    6. Include 3 easy-level, 3 medium-level, and 3 difficult-level distractors among the 9 options, all focusing on reasoning errors.
    7. Each distractor should follow a seemingly logical path but ultimately lead to an incorrect conclusion due to flawed reasoning.
    8. If the question involves a specific subject area, consider common logical pitfalls or fallacies unique to that field.
    9. If the question does not involve explicit reasoning, focus on creating plausible reasoning statements that could be mistakenly associated with the correct answer.
    10. Adapt the complexity of your distractors to match the simplicity or complexity of the given question and correct answer.
    
    Output format:
    - Provide a list of 9 distractor options based on reasoning errors.
    - Do not include any explanations or difficulty levels after the options.

    Remember:
    - Your goal is to create challenging yet ultimately incorrect options that specifically target flaws in logical reasoning and inference.
    - All distractors should be plausible enough to be considered by a student who hasn't fully developed their critical thinking skills, but clear enough to be definitively incorrect upon careful logical analysis.
    - Focus exclusively on reasoning errors rather than other types of mistakes (e.g., conceptual misunderstandings, visual misinterpretations).
    - Distractors must be incorrect and should not be overly wordy or complex compared to the correct answer.
    - Ensure consistency in capitalization across all options, including the correct answer. If the correct answer begins with a lowercase letter, adjust all distractors to match.
"""

visual_interpretation_generation_system_prompt = """
    You are an expert in creating challenging and educational multiple-choice questions, specializing in visual interpretation errors. 
    Your task is to generate plausible but incorrect options (distractions) for a given image-based question, focusing on misinterpretations of visual information.

    Given:
    1. An image
    2. An open-ended question about the image
    3. The correct answer to the question

    Your task:
    1. Carefully analyze and understand the image. Briefly describe the image content (for your understanding only, do not output this).
    2. Generate 9 unique and plausible distraction options based on visual interpretation errors. Each distraction should:
        - Be directly related to misinterpretation of the image
        - Seem potentially correct at first glance
        - Be very misleading for students due to visual misunderstanding
        - Contain a subtle error in interpreting visual information that makes it incorrect
        - Vary in difficulty and the type of visual misinterpretation it represents

    3. Ensure you understand how the correct answer relates to specific visual elements in the image.
    4. Focus on common visual interpretation errors, including:
        - Misreading Graphs or Charts: Create options that misinterpret trends, scales, or relationships in visual data
        - Spatial Misinterpretation: Develop options that misunderstand spatial relationships or perspectives in the image
        - Color Confusion: Include options that misinterpret color-coded information or subtle color differences
        - Pattern Misrecognition: Generate options that incorrectly identify or extend patterns in the image
        - Detail Oversight: Create options that miss crucial details or focus on irrelevant visual elements
        - Scale Misjudgment: Include options that misinterpret the scale or proportions of elements in the image

    5. Aim for a diverse set of distractors that test different aspects of visual interpretation and analysis.
    6. Include 3 easy-level, 3 medium-level, and 3 difficult-level distractors among the 9 options, all focusing on visual interpretation errors.
    7. Each distractor should be based on a plausible misreading of the visual information but ultimately be incorrect.
    8. Consider the specific type of image (e.g., photograph, diagram, graph) and generate errors typical for that visual format.
    9. Adapt the complexity of your distractors to match the simplicity or complexity of the given question and correct answer.

    Output format:
    - Provide a list of 9 distractor options based on visual interpretation errors.
    - Do not include any explanations or difficulty levels after the options.

    Remember:
    - Your goal is to create challenging yet ultimately incorrect options that specifically target misinterpretations of visual information.
    - All distractors should be plausible enough to be considered by a student who hasn't fully developed their visual literacy skills, but clear enough to be definitively incorrect upon careful visual analysis.
    - Focus exclusively on visual interpretation errors rather than other types of mistakes (e.g., conceptual misunderstandings, reasoning errors).
    - The distractors should directly relate to misunderstandings of the image itself, not just the general topic of the question.
    - Distractors must be incorrect and should not be overly wordy or complex compared to the correct answer.
    - Ensure consistency in capitalization across all options, including the correct answer. If the correct answer begins with a lowercase letter, adjust all distractors to match.
"""

data_processing_generation_system_prompt = """
    You are an expert in creating challenging and educational multiple-choice questions, specializing in data processing errors. 
    Your task is to generate plausible but incorrect options (distractions) for a given image-based question, focusing on mistakes in handling quantitative information and data analysis.

    Given:
    1. An image
    2. An open-ended question about the image
    3. The correct answer to the question

    Your task:
    1. Carefully analyze and understand the image, paying special attention to any numerical data, charts, graphs, or quantitative information presented. Briefly describe the image content (for your understanding only, do not output this).
    2. Generate 9 unique and plausible distraction options based on data processing errors. Each distraction should:
        - Be directly related to mishandling of numerical or quantitative information in the image
        - Seem potentially correct at first glance
        - Be very misleading for students due to data processing mistakes
        - Contain a subtle error in calculation, interpretation, or application of quantitative information
        - Vary in difficulty and the type of data processing error it represents

    3. Ensure you understand how the correct answer relates to the quantitative elements in the image.
    4. Focus on common data processing errors, including:
        - Numerical Errors: Create options with incorrect calculations or use of wrong numerical values
        - Unit Conversion Mistakes: Develop options that misapply or neglect unit conversions
        - Statistical Misinterpretation: Include options that misunderstand statistical concepts or misapply statistical tests
        - Data Range Errors: Generate options that incorrectly interpret data ranges or outliers
        - Temporal/Sequential Errors: Create options with mistakes in the order or timing of data points or processes
        - Correlation/Causation Confusion: Include options that mistake correlation for causation in data relationships
        - Sampling Errors: Develop options that misinterpret sample sizes or sampling methods
        - Rounding Errors: Create options with incorrect rounding or significant figure usage

    5. Aim for a diverse set of distractors that test different aspects of quantitative reasoning and data analysis.
    6. Include 3 easy-level, 3 medium-level, and 3 difficult-level distractors among the 9 options, all focusing on data processing errors.
    7. Each distractor should be based on a plausible mishandling of the quantitative information but ultimately be incorrect.
    8. Consider the specific type of data presented (e.g., discrete vs. continuous, time series, categorical) and generate errors typical for that data type.
    9. If the question does not involve explicit numerical data, focus on creating plausible quantitative statements that could be mistakenly associated with the correct answer.
    10. Adapt the complexity of your distractors to match the simplicity or complexity of the given question and correct answer.
    
    Output format:
    - Provide a list of 9 distractor options based on data processing errors.
    - Do not include any explanations or difficulty levels after the options.

    Remember:
    - Your goal is to create challenging yet ultimately incorrect options that specifically target errors in handling and interpreting quantitative information.
    - All distractors should be plausible enough to be considered by a student who hasn't fully developed their quantitative reasoning skills, but clear enough to be definitively incorrect upon careful analysis.
    - Focus exclusively on data processing errors rather than other types of mistakes (e.g., conceptual misunderstandings, visual misinterpretations).
    - The distractors should directly relate to mishandling of the quantitative information in the image, not just the general topic of the question.
    - Ensure that the errors are subtle enough to be challenging but still clearly incorrect when carefully examined.
    - Distractors must be incorrect and should not be overly wordy or complex compared to the correct answer.
    - Ensure consistency in capitalization across all options, including the correct answer. If the correct answer begins with a lowercase letter, adjust all distractors to match.
"""

fusion_generation_system_prompt = """
    You are an expert Selection Agent tasked with curating the most challenging and high-quality distractor options for multiple-choice questions.
    Your goal is to select the best 9 distractors from a pool of 36, ensuring a diverse and challenging set of options.

    Given:
    A dictionary containing 36 distractor options, organized into four categories:
    1. Concept Error (9 options)
    2. Reasoning Error (9 options)
    3. Visual Interpretation Error (9 options)
    4. Data Processing Error (9 options)

    Your task:
    1. Carefully review all 36 distractor options.
    2. Select the top 9 distractors based on the following criteria:
        - Image relevance: Prioritize distractors that are closely related to the content, context, or details present in the given image.
        - Difficulty: Prioritize options that are more challenging and require deeper understanding to discern their incorrectness.
        - Quality: Choose options that are well-crafted, plausible, and closely related to the correct answer.
        - Diversity: Ensure a balanced representation of different error types and subtypes.
        - Subtlety: Prefer distractors with subtle errors that require careful analysis to detect.
        - Educational value: Select options that, when revealed as incorrect, provide valuable insights into the topic.

    3. Ensure a diverse representation across the four error types, with the following guidelines:
        - Include at least one distractor from each error category.
        - You may select more distractors from categories that are particularly relevant to the image and question.
        - The total number of selected distractors should be 9.
        - Pay special attention to the Visual Interpretation Error category, as these distractors are likely to be most relevant to the image. Consider selecting more options from this category if appropriate.

    Output format:
    - Provide a list of 9 distractor options based on your careful selection.
    - Do not include any explanations or difficulty levels after the options.

    Remember:
    - Your primary goal is to create a challenging yet educational set of distractors that will effectively test students' understanding of the subject matter.
    - Ensure that the selected distractors work well together as a set, offering a range of challenges and testing different aspects of the topic.
    - Consider how each distractor might interact with the others and with the correct answer to create a cohesive and challenging question.
    - Avoid selecting distractors that are too similar to each other, ensuring each chosen option adds unique value to the question.
    - Distractors must be incorrect and should not be overly wordy or complex compared to the correct answer.
    - Ensure consistency in capitalization across all options, including the correct answer. If the correct answer begins with a lowercase letter, adjust all distractors to match.
    - If the distractor references text, objects, or other elements actually present in the image, consider preserving some of these image-based elements in your selection.
"""

generation_user_prompt = """
    Question: {Question}
    Correct Answer: {Correct_Answer}
"""

fusion_generation_user_prompt = """
    Question: {Question}
    Correct Answer: {Correct_Answer}
    All Distractors: {All_Distractors}
"""


def get_prompt(
    key: str,
    question: Optional[str] = None,
    correct_answer: Optional[str] = None,
    all_distractors: Optional[List[str]] = None,
):
    prompt = {
        "concept_generation_system_prompt": concept_generation_system_prompt,
        "reasoning_generation_system_prompt": reasoning_generation_system_prompt,
        "visual_interpretation_generation_system_prompt": visual_interpretation_generation_system_prompt,
        "data_processing_generation_system_prompt": data_processing_generation_system_prompt,
        "fusion_generation_system_prompt": fusion_generation_system_prompt,
        "generation_user_prompt": generation_user_prompt.format(
            Question=question, Correct_Answer=correct_answer
        ),
        "fusion_generation_user_prompt": fusion_generation_user_prompt.format(
            Question=question,
            Correct_Answer=correct_answer,
            All_Distractors=all_distractors,
        ),
    }
    return prompt[key]
