from pydantic import BaseModel
from typing import Optional, List, Dict

class LoginRequest(BaseModel):
    """
    Login Request Model
    """
    username:str
    password:str

class QueryRequest(BaseModel):
    """
    Query Request Model
    """
    question:str
    context_length:Optional[int] = 2

class QueryResponse(BaseModel):
    """
    Query Response Model
    """
    question:str
    answer:str
    cached:bool
    response_time:float
    user:str

class HealthResponse(BaseModel):
    """
    Health Check response
    """
    status: str
    query_engine_initialized: bool
    cached_queries:int

class DashBoardResponse(BaseModel):
    """
    Dashboard metrics Response
    """
    status:str
    user:str
    role:str
    total_queries:int
    total_users:int
    cached_queries:int
    avg_response_time:float

class TokenResponse(BaseModel):
    """
    Token Response Model
    """
    access_token:str
    token_type:str
    role:str

class HistoryResponse(BaseModel):
    """
    Query History Response
    """
    user: str
    query_count:int
    history:List[Dict]