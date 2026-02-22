import os
import sys
import logging
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.graph_engine import AgenticRAGEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_inference():
    logger.info("STARTING AGENTIC RAG INFERENCE")
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("OPENAI_API_KEY not found")
        sys.exit(1)

    try:
        engine = AgenticRAGEngine(llm_api_key=api_key)
        test_question = "Are there any information about Donald Trump?"
        
        logger.info(f"USER QUERY: '{test_question}'")
        final_answer = engine.run(test_question)
        print("\n" + "="*60)
        print("FINAL AI ANSWER:")
        print("="*60)
        print(final_answer)
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"An error occurred during graph execution: {e}")

if __name__ == "__main__":
    run_inference()