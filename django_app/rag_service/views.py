import json
import os
import logging
import datetime
import jwt
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from core.graph_engine import AgenticRAGEngine
logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

JWT_SECRET = settings.SECRET_KEY

JWT_ALGORITHM = 'HS256'
SYSTEM_PASSCODE = 'dikhang_rag_demo'
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
def login_endpoint(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed."}, status=405)
        
    try:
        body = json.loads(request.body)
        passcode = body.get("passcode", "").strip()
        
        if passcode == SYSTEM_PASSCODE:
            payload = {
                'user': 'guest_user',
                'exp': datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
                'iat': datetime.now(datetime.timezone.utc)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            return JsonResponse({"token": token, "message": "Authentication successful"}, status=200)
        else:
            return JsonResponse({"error": "Invalid passcode."}, status=401)
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({"error": "Server error during authentication."}, status=500)
    
@csrf_exempt
def chat_endpoint(request):
    if request.method == "POST":
        if not rag_engine:
            return JsonResponse({"error": "System is currently unavailable (Engine failed to load)."}, status=503)

        try:
            body = json.loads(request.body)
            question = body.get("question", "").strip()
            # password = body.get("password", "").strip()
            
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