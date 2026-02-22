import json
import os
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from core.graph_engine import AgenticRAGEngine
logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

try:
    logger.info("Initializing AgenticRAGEngine for Django App...")
    rag_engine = AgenticRAGEngine(llm_api_key=API_KEY)
    logger.info("Engine loaded successfully into memory.")
except Exception as e:
    logger.error(f"Failed to load RAG Engine: {e}")
    rag_engine = None

def home_view(request):
    return render(request, 'rag_service/home.html')

def contact_view(request):
    return render(request, 'rag_service/contact.html')

def app_view(request):
    return render(request, 'rag_service/app.html')

@csrf_exempt
def chat_endpoint(request):
    if request.method == "POST":
        if not rag_engine:
            return JsonResponse({"error": "System is currently unavailable (Engine failed to load)."}, status=503)

        try:
            body = json.loads(request.body)
            question = body.get("question", "").strip()

            if not question:
                return JsonResponse({"error": "Question field cannot be empty."}, status=400)

            logger.info(f"API Received Question: {question}")
            
            # Execute the LangGraph workflow
            answer = rag_engine.run(question)
            
            return JsonResponse({
                "question": question,
                "answer": answer,
                "status": "success"
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"Error": "Invalid JSON payload."}, status=400)
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return JsonResponse({"error": "Internal server error processing your query."}, status=500)
            
    return JsonResponse({"Error": "Method not allowed. Use POST."}, status=405)