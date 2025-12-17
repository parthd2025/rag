"""
Quiz generation utilities for building questionnaires from existing chunks.
Uses the existing LLM engine via a simple helper function.
"""

from typing import List, Dict, Any

from logger_config import logger


def build_quiz_prompt(context_chunks: List[str], num_questions: int = 5) -> str:
    """
    Build a prompt instructing the LLM to create a quiz from the given context.

    Args:
        context_chunks: List of text chunks to use as source material
        num_questions: Number of questions to generate

    Returns:
        Prompt string
    """
    joined_context = "\n\n".join(context_chunks[:15])  # Increased to 15 for more context

    prompt = f"""You are an educational content creator designing a multiple-choice quiz based on provided document content.

Your task: Create {num_questions} engaging and varied multiple-choice questions that test understanding of the material.

Context from documents:
{joined_context}

Instructions for question creation:
1. Create questions that test key concepts, facts, and understanding from the provided content
2. Questions should be clear and unambiguous
3. Each question must have 4 distinct options (A, B, C, D)
4. Ensure one option is clearly the correct answer
5. The correct answer should always be directly supported by the context
6. Create plausible but incorrect alternatives (distractors)
7. Include questions that cover different parts of the provided content

Return ONLY valid JSON (no additional text) with this exact structure:
{{
  "questions": [
    {{
      "question": "What is the main topic?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_index": 0,
      "explanation": "Brief explanation of why this is correct based on the context."
    }}
  ]
}}

Requirements:
- Each question MUST be answerable from the provided context
- Provide exactly {num_questions} questions
- Ensure valid JSON format
- Do NOT include any text before or after the JSON
"""
    return prompt


def generate_quiz_from_chunks(
    llm_engine,
    chunks: List[str],
    num_questions: int = 5,
) -> Dict[str, Any]:
    """
    Generate a quiz JSON structure from existing chunks using the LLM engine.

    Args:
        llm_engine: LLM engine instance with a .generate(prompt, max_tokens, temperature) method
        chunks: List of chunks to use as source material
        num_questions: Number of questions to generate

    Returns:
        Dict with keys:
            - questions: list of question objects, or empty list on failure
            - raw: raw LLM response (for debugging)
    """
    import json

    if not chunks:
        return {"questions": [], "raw": ""}

    prompt = build_quiz_prompt(chunks, num_questions=num_questions)

    try:
        logger.info(f"QUIZ: Generating quiz with {num_questions} questions from {len(chunks)} chunk(s)")
        raw = llm_engine.generate(prompt, max_tokens=3000, temperature=0.7)

        # Try to parse JSON from the response, even if there is stray text
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            raw_json = raw[start : end + 1]
        else:
            raw_json = raw

        try:
            data = json.loads(raw_json)
            questions = data.get("questions", [])
        except json.JSONDecodeError as je:
            logger.error(f"QUIZ: Failed to parse JSON response: {je}")
            logger.debug(f"QUIZ: Raw response: {raw[:500]}...")
            return {"questions": [], "raw": raw}

        # Basic validation
        cleaned_questions = []
        for q in questions:
            question_text = q.get("question", "").strip()
            options = q.get("options", [])
            correct_index = q.get("correct_index", 0)
            explanation = q.get("explanation", "").strip()

            if not question_text or not options:
                continue

            if not (0 <= int(correct_index) < len(options)):
                correct_index = 0

            cleaned_questions.append(
                {
                    "question": question_text,
                    "options": options,
                    "correct_index": int(correct_index),
                    "explanation": explanation,
                }
            )

        return {"questions": cleaned_questions, "raw": raw}
    except Exception as e:
        logger.error(f"QUIZ: Failed to generate quiz: {e}", exc_info=True)
        return {"questions": [], "raw": ""}


