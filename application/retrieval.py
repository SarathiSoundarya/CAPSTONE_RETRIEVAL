import os
import asyncio
from dotenv import load_dotenv
from llama_index.core import Document, VectorStoreIndex
from llama_index.llms.openai import OpenAI
from data import load_csv
import logging
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
import traceback
load_dotenv()
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("Capstone retrieval")
query_engine = None
index_initialized = None
api_key = os.getenv("AZURE_OPENAI_KEY")
api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_VERSION")
model_name =  "gpt-4o-mini"

llm = AzureOpenAI(
            model="gpt-4.1-mini",
            deployment_name=model_name,
            api_key=api_key,
            azure_endpoint=api_endpoint,
            api_version=api_version,
        )
      
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="text-embedding-ada-002",
    api_key=api_key,
    azure_endpoint=api_endpoint,
    api_version=api_version,
)
        
Settings.llm = llm
Settings.embed_model = embed_model

def build_index():
    global query_engine, index_initialized
    try:
        logger.info("Starting vectir index build...")
        df = load_csv()
        docs = [Document(text=row["text"]) for _, row in df.iterrows()]
        index = VectorStoreIndex.from_documents(docs)

        query_engine = index.as_query_engine()
        index_initialized = True
        return query_engine
    
    except Exception as err:
        logger.error(f"Error building index:{str(err)}, with traceback:{traceback.format_exc()}")
        index_initialized = False
        return None

def initialize_retrieval():
    global query_engine, index_initialized
    try:
        query_engine = build_index()
        index_initialized = False
    except Exception as err:
        logger.error("Failed to initialize retrieval")
        index_initialized = False

def execute_query(question:str):
    try:
        response = query_engine.query(question)
        logger.info(f"Returning response:{response}")
        return str(response)
    except Exception as err:
        logger.error(f"Error executing query:{str(err)}")