"""
Extract and list questions from quiz/questionnaire patterns.
"""

import json
from typing import List, Dict, Any
from backend.quiz import generate_quiz_from_chunks
from backend.llm_loader import get_llm_engine
from backend.vectorstore import FAISSVectorStore
from backend.config import settings
from backend.logger_config import logger


def extract_questions_only(quiz_data: Dict[str, Any]) -> List[str]:
    """
    Extract only the questions from quiz data.
    
    Args:
        quiz_data: Dictionary containing questions list
        
    Returns:
        List of question strings
    """
    questions = []
    for item in quiz_data.get("questions", []):
        question_text = item.get("question", "").strip()
        if question_text:
            questions.append(question_text)
    return questions


def print_questions_list(questions: List[str]) -> None:
    """
    Print questions in a clean list format.
    
    Args:
        questions: List of question strings
    """
    print("\n" + "="*80)
    print(f"QUESTIONS LIST ({len(questions)} questions)")
    print("="*80 + "\n")
    
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
    
    print("\n" + "="*80 + "\n")


def get_questions_from_vectorstore(num_questions: int = 5) -> List[str]:
    """
    Generate quiz from stored documents and return questions only.
    
    Args:
        num_questions: Number of questions to generate
        
    Returns:
        List of question strings
    """
    try:
        # Load LLM engine
        llm_engine = get_llm_engine()
        
        # Load vector store
        vector_store = FAISSVectorStore(
            embedding_model_name=settings.EMBEDDING_MODEL,
            index_path=settings.INDEX_PATH,
            metadata_path=settings.METADATA_PATH
        )
        
        logger.info(f"Loaded {len(vector_store.chunks)} chunks from vector store")
        
        if not vector_store.chunks:
            print("⚠️ No chunks found in vector store!")
            return []
        
        # Generate quiz
        quiz_data = generate_quiz_from_chunks(
            llm_engine,
            vector_store.chunks[:20],  # Use first 20 chunks
            num_questions=num_questions
        )
        
        # Extract questions
        questions = extract_questions_only(quiz_data)
        
        return questions
        
    except Exception as e:
        logger.error(f"Error generating questions: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    import sys
    
    num_questions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    print(f"\n🔍 Generating {num_questions} questions from documents...\n")
    
    questions = get_questions_from_vectorstore(num_questions=num_questions)
    
    if questions:
        print_questions_list(questions)
        
        # Save to file
        output_file = "questions_list.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"QUESTIONS LIST ({len(questions)} questions)\n")
            f.write("="*80 + "\n\n")
            for i, q in enumerate(questions, 1):
                f.write(f"{i}. {q}\n")
        
        print(f"✅ Questions saved to: {output_file}\n")
    else:
        print("❌ Failed to generate questions\n")
