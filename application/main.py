import logging
import os
import time
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging
from retrieval import initialize_retrieval, execute_query
from auth import (get_current_user, require_admin, create_access_token, users_db)
from models import (LoginRequest, QueryRequest, QueryResponse, HealthResponse, DashBoardResponse, TokenResponse, HistoryResponse)
from analytics import (track_request, cache_query, get_cached_query, get_user_history, get_analytics_summary)
import traceback
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("capstone_main")

app = FastAPI(title="Capstone AI Pipeline", version=2.0, description="Advanced AI Pipeline with Auth and monitoring")

# static_dir = os.path.join(os.path.dirname(__file__),"static")
# if os.path.exists(static_dir):

@app.on_event("startup")
async def startup_event():
    """
    Initialize retrieval system on app start
    """
    initialize_retrieval()
    logger.info("App started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on app shutdown
    """
    logger.info("App shutdown")

###AUTHENTICATION ENDPOINTS###################
@app.post("/token", response_model=TokenResponse)
async def login(credentials:LoginRequest):
    user = users_db.get(credentials.username)
    if not user or user["password"]!= credentials.password:
        logger.warning(f"Failed login attempt for user:{user}")
    access_token = create_access_token({"sub":credentials.username,"role":user["role"]})
    logger.info(f"User {credentials.username} logged in sucessfully!")
    return {
        "access_token":access_token, 
        "token_type":"bearer",
        "role":user["role"]
    }

@app.post("/ask",response_model= QueryResponse)
async def ask_question(request:QueryRequest, user:dict = Depends(get_current_user)):
    start_time = time.time()
    cache_key = f"{request.question}:{user['username']}"
    cached_result = get_cached_query(cache_key)
    if cached_result:
        logger.info(f"Cache hit for query:{request.question}")
        return {
            "question":request.question, 
            "answer":cached_result["answer"],
            "cached":True,
            "response_time":0.001,
            "user":user["username"]
        }
    try:
        logger.info(f"User {user['username']} asked: {request.question}")
        answer = execute_query(request.question)
        cache_query(cache_key, answer, user["username"])
        elapsed_time = time.time() - start_time
        track_request(user["username"],request.question,answer, elapsed_time)
        return {
            "question":request.question,
            "answer":answer,
            "cached":False,
            "response_time":elapsed_time,
            "user":user["username"]
        }
    except Exception as err:
        logger.error(f"Error processing the query:{str(err)} with traceback:{traceback.format_exc()}")

@app.get("/history", response_model=HistoryResponse)
async def get_history(user:dict = Depends(get_current_user)):
    """
    Get query history for current user
    """
    history = get_user_history(user["username"])
    return {
        "user":user["username"],
        "query_count":len(history),
        "history":history[-10:]
    }

@app.get("/dashboard", response_model=DashBoardResponse)
async def dashboard(user:dict = Depends(get_current_user)):
    analytics = get_analytics_summary()
    return {
        "status":"Pipeline running",
        "user":user["username"],
        "role":user["role"],
        "total_queries":analytics["total_queries"],
        "total_users":analytics["total_users"],
        "cached_queries":analytics["cached_queries"],
        "avg_response_time":analytics["avg_response_time"]
    }

@app.get("/admin/stats")
async def admin_stats(user:dict = Depends(require_admin)):
    analytics = get_analytics_summary()
    return {
        "admin":user["username"],
        "total_requests":analytics["total_requests"],
        "cached_queries":analytics["cached_queries"],
        "cache_size":analytics["cache_size"],
        "avg_response_time":analytics["avg_response_time"]
    }

@app.get("/",response_class=FileResponse)
async def landing_page():
    """
    Serve the landing page HTML.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file =  os.path.join(current_dir, "static", "index.html")
    logger.info(f"Attempting to serve:{html_file}")
    logger.info(f"File exists:{os.path.exists(html_file)}")
    if os.path.exists(html_file):
        return html_file
    else:
        logger.error("HTML file not found at locations")