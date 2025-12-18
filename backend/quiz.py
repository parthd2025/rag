"""
Suggested questions generation utilities for RAG chatbot.
Implements hybrid approach: comparative questions + document-specific questions.
"""

from typing import List, Dict, Any

from logger_config import logger


def build_comparative_questions_prompt(context_chunks: List[str], num_documents: int = 2) -> str:
    """
    Build a prompt for generating comparative questions across multiple documents.

    Args:
        context_chunks: List of text chunks from multiple documents
        num_documents: Number of documents being analyzed

    Returns:
        Prompt string
    """
    joined_context = "\n\n".join(context_chunks[:20])

    prompt = f"""You are an expert at creating insightful comparative questions for multi-document analysis.

Your task: Create 3-4 comparative questions that help users understand relationships and differences across the {num_documents} provided documents.

Context from documents:
{joined_context}

Instructions:
1. Create questions that require cross-document analysis
2. Questions should highlight key differences, similarities, or complementary information
3. Questions should be clear and valuable for understanding the full picture
4. Each question should be direct and answerable from the provided content
5. Focus on: contradictions, complementary info, common themes, key differences

Return ONLY valid JSON (no additional text):
{{
  "comparative_questions": [
    "Question that compares across documents?",
    "What are the key differences between...?",
    "How do these documents complement each other?"
  ]
}}

Requirements:
- Provide 3-4 questions only
- Questions should be open-ended (no multiple choice options)
- Ensure valid JSON format
"""
    return prompt


def build_document_specific_prompt(chunks: List[str], document_name: str, num_questions: int = 2) -> str:
    """
    Build a prompt for generating questions specific to one document.

    Args:
        chunks: Chunks from a specific document
        document_name: Name of the document
        num_questions: Number of questions to generate

    Returns:
        Prompt string
    """
    joined_context = "\n\n".join(chunks[:10])

    prompt = f"""You are an expert at creating focused questions about document content.

Your task: Create {num_questions} key questions that help users understand the main points in this document: {document_name}

Document content:
{joined_context}

Instructions:
1. Create questions that highlight main topics and key information
2. Questions should be direct and answerable from the document
3. Focus on actionable, valuable information
4. Questions should be open-ended (no multiple choice)
5. Avoid generic questions - be specific to this document

Return ONLY valid JSON (no additional text):
{{
  "questions": [
    "Key question about this document?",
    "Another important question?"
  ]
}}

Requirements:
- Provide exactly {num_questions} questions
- Ensure valid JSON format
"""
    return prompt


def generate_comparative_questions(
    llm_engine,
    chunks: List[str],
    num_documents: int = 2,
) -> List[str]:
    """
    Generate comparative questions across multiple documents.

    Args:
        llm_engine: LLM engine instance
        chunks: Chunks from all documents
        num_documents: Number of documents

    Returns:
        List of comparative question strings
    """
    import json

    if not chunks:
        return []

    prompt = build_comparative_questions_prompt(chunks, num_documents)

    try:
        logger.info(f"QUESTIONS: Generating comparative questions from {num_documents} documents")
        raw = llm_engine.generate(prompt, max_tokens=2000, temperature=0.7)

        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            raw_json = raw[start : end + 1]
        else:
            raw_json = raw

        data = json.loads(raw_json)
        questions = data.get("comparative_questions", [])
        return [q.strip() for q in questions if q.strip()]
    except Exception as e:
        logger.error(f"QUESTIONS: Failed to generate comparative questions: {e}")
        return []


def generate_document_specific_questions(
    llm_engine,
    chunks: List[str],
    document_name: str,
    num_questions: int = 2,
) -> List[str]:
    """
    Generate questions specific to one document.

    Args:
        llm_engine: LLM engine instance
        chunks: Chunks from the document
        document_name: Name of the document
        num_questions: Number of questions to generate

    Returns:
        List of question strings
    """
    import json

    if not chunks:
        return []

    prompt = build_document_specific_prompt(chunks, document_name, num_questions)

    try:
        logger.info(f"QUESTIONS: Generating {num_questions} questions for {document_name}")
        raw = llm_engine.generate(prompt, max_tokens=1500, temperature=0.7)

        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            raw_json = raw[start : end + 1]
        else:
            raw_json = raw

        data = json.loads(raw_json)
        questions = data.get("questions", [])
        return [q.strip() for q in questions if q.strip()]
    except Exception as e:
        logger.error(f"QUESTIONS: Failed to generate questions for {document_name}: {e}")
        return []


def generate_suggested_questions_hybrid(
    llm_engine,
    chunks: List[str],
    num_documents: int = 1,
) -> Dict[str, Any]:
    """
    Generate hybrid suggested questions: comparative + document-specific.

    Args:
        llm_engine: LLM engine instance
        chunks: All chunks available
        num_documents: Number of documents

    Returns:
        Dict with comparative_questions and document_questions
    """
    result = {
        "comparative_questions": [],
        "document_questions": {},
        "questions": []  # Flattened for backward compatibility
    }

    if not chunks:
        return result

    # Generate comparative questions if multiple documents
    if num_documents > 1:
        comparative = generate_comparative_questions(llm_engine, chunks[:30], num_documents)
        result["comparative_questions"] = comparative
        result["questions"].extend(comparative)

    return result


def generate_quiz_from_chunks(
    llm_engine,
    chunks: List[str],
    num_questions: int = 5,
) -> Dict[str, Any]:
    """
    Backward-compatible wrapper for generating suggested questions.
    Generates comparative questions from provided chunks.

    Args:
        llm_engine: LLM engine instance
        chunks: Chunks to generate questions from
        num_questions: Number of questions (used for count estimation)

    Returns:
        Dict with questions list for backward compatibility
    """
    if not chunks:
        return {"questions": []}

    try:
        logger.info(f"QUIZ: Generating {num_questions} suggested questions from {len(chunks)} chunks")
        
        # Generate comparative questions
        comparative = generate_comparative_questions(llm_engine, chunks, num_documents=1)
        
        # Convert list of strings to list of dicts for frontend
        question_dicts = []
        for idx, q in enumerate(comparative, 1):
            question_dicts.append({
                "question": q,
                "type": "comparative"
            })
        
        # Return in format expected by frontend
        return {
            "questions": question_dicts if question_dicts else [],
            "raw": ""
        }
    except Exception as e:
        logger.error(f"QUIZ: Failed to generate questions: {e}", exc_info=True)
        return {"questions": [], "raw": ""}


