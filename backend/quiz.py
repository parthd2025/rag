"""
Suggested questions generation utilities for RAG chatbot.
Implements hybrid approach: comparative questions + document-specific questions.
"""

from typing import List, Dict, Any, Optional, Set

from logger_config import logger


def build_comparative_questions_prompt(
    context_chunks: List[str],
    num_documents: int = 2,
    target_questions: int = 4
) -> str:
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

Your task: Create up to {target_questions} comparative questions that help users understand relationships and differences across the {num_documents} provided documents.

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
- Provide no more than {target_questions} questions (fewer is acceptable if context is limited)
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
    max_questions: int = 4,
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

    prompt = build_comparative_questions_prompt(chunks, num_documents, target_questions=max_questions)

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
        trimmed = [q.strip() for q in questions if q.strip()]
        return trimmed[:max_questions]
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
    metadata: Optional[List[dict]] = None,
    num_questions: int = 5,
    max_questions_single: int = 10,
    max_questions_multi: int = 20,
) -> Dict[str, Any]:
    """Generate suggested questions, balancing comparative and document-specific prompts."""
    if not chunks:
        return {
            "questions": [],
            "comparative_questions": [],
            "document_questions": {},
            "requested": num_questions,
            "limit": 0,
            "document_count": 0,
        }

    try:
        logger.info(
            "QUIZ: Generating %s suggested questions from %s chunks",
            num_questions,
            len(chunks)
        )

        # Align metadata with chunks when provided
        doc_chunks: Dict[str, List[str]] = {}
        if metadata and len(metadata) == len(chunks):
            for chunk, meta in zip(chunks, metadata):
                doc_name = "Document"
                if meta:
                    doc_name = meta.get("source_doc") or meta.get("document") or "Document"
                doc_chunks.setdefault(doc_name, []).append(chunk)
        else:
            doc_chunks = {"Document": chunks}

        document_count = max(1, len(doc_chunks))
        question_limit = max(
            1,
            min(
                int(num_questions or 1),
                max_questions_multi if document_count > 1 else max_questions_single,
            ),
        )

        questions: List[Dict[str, Any]] = []
        comparative: List[str] = []
        document_questions: Dict[str, List[str]] = {}
        used_text: Set[str] = set()

        # Comparative set for multi-document scenario
        if document_count > 1:
            comparative_target = min(4, question_limit)
            comparative = generate_comparative_questions(
                llm_engine,
                chunks,
                num_documents=document_count,
                max_questions=comparative_target,
            )
            for question in comparative:
                if question and question not in used_text and len(questions) < question_limit:
                    questions.append({
                        "question": question,
                        "type": "comparative"
                    })
                    used_text.add(question)

        # Document-specific questions
        remaining = question_limit - len(questions)
        if remaining > 0:
            doc_names = list(doc_chunks.keys())

            if document_count == 1:
                doc_name = doc_names[0]
                desired = remaining
                generated = generate_document_specific_questions(
                    llm_engine,
                    doc_chunks[doc_name],
                    doc_name,
                    num_questions=desired,
                )
                document_questions[doc_name] = generated
                for question in generated:
                    if question and question not in used_text and len(questions) < question_limit:
                        questions.append({
                            "question": question,
                            "type": "document",
                            "document": doc_name,
                        })
                        used_text.add(question)
            else:
                base = remaining // document_count
                extra = remaining % document_count
                for idx, doc_name in enumerate(doc_names):
                    if len(questions) >= question_limit:
                        break

                    target = base + (1 if idx < extra else 0)
                    if target <= 0:
                        target = 1 if len(questions) < question_limit else 0
                    target = min(target, question_limit - len(questions))
                    if target <= 0:
                        continue

                    generated = generate_document_specific_questions(
                        llm_engine,
                        doc_chunks[doc_name],
                        doc_name,
                        num_questions=target,
                    )
                    document_questions[doc_name] = generated
                    for question in generated:
                        if question and question not in used_text and len(questions) < question_limit:
                            questions.append({
                                "question": question,
                                "type": "document",
                                "document": doc_name,
                            })
                            used_text.add(question)

        return {
            "questions": questions,
            "comparative_questions": comparative,
            "document_questions": document_questions,
            "requested": num_questions,
            "limit": question_limit,
            "document_count": document_count,
        }

    except Exception as exc:
        logger.error("QUIZ: Failed to generate questions: %s", exc, exc_info=True)
        return {
            "questions": [],
            "comparative_questions": [],
            "document_questions": {},
            "requested": num_questions,
            "limit": 0,
            "document_count": 0,
        }


