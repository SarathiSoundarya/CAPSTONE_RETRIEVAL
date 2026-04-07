import time
import os
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import logging
from dotenv import load_dotenv
load_dotenv()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("capstone analytics")

request_history: Dict[str, List[Dict]] = defaultdict(list)
query_cache: Dict[str, Dict]= {}

def track_request(username:str, question:str, answer:str, response_time:float):
    """
    Track user request for analytics
    """
    request_history[username].append({
        "question":question, 
        "timestamp":datetime.utcnow(),
        "answer":answer,
        "response_time":response_time
    })
    logger.info("Request tracked for {username}")

def cache_query(cache_key:str, answer:str, username:str):
    query_cache["cache_key"]={
        "answer":answer, 
        "timestamp":datetime.utcnow(), 
        "user":username
    }
    logger.info(f"Query cached with key:{cache_key}")

def get_cached_query(cache_key):
    return request_history.get(cache_key)

def get_user_history(username):
    return request_history.get(username, [])

def get_analytics_summary():
    total_queries = sum(len(queries) for queries in request_history.values())
    total_users = len(request_history)
    avg_response_time = 0
    all_times = []
    for queries in request_history.values():
        all_times.extend([q.get("response_time",0) for q in queries])

    if all_times:
        avg_response_time = sum(all_times)/len(all_times)
    return {
        "total_queries":total_queries, 
        "total_users":total_users, 
        "cached_queries":len(query_cache), 
        "avg_response_time":round(avg_response_time), 
        "cache_size":sum(len(str(v)) for v in query_cache.values())
    }

def clear_old_cache(max_age_seconds = 3600):
    now = datetime.now()
    keys_to_remove = []
    for key, val in query_cache.items():
        age = (now-val["timestamp"]).total_seconds()
        if age>=max_age_seconds:
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del query_cache[key]
    logger.info(f"Cleared {len(keys_to_remove)} old cache entries")