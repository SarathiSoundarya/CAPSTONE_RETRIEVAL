import os
import pandas  as pd
from functools import lru_cache
import logging
from dotenv import load_dotenv
from fastapi import HTTPException
load_dotenv()

logger = logging.getLogger("capstone_data")
@lru_cache(maxsize=1) #this ensures data is not loaded again and again. It caches the result of the function load_csv(). Since function takes no args, there is only one possible value
def load_csv():
    """
    load and cache csv data with extended documentation
    """
    try:
        df = pd.DataFrame(
            {
                "id":[1,2,3,4,5,6,7], 
                "text":[
                    "Python is great for data science and ML!",
                    "FASTAPIs makes building REST APIs easy!", 
                    "LlamaIndex enables semantic search over your data.", 
                    "Docker helps you deploy applications anywhere consistently.", 
                    "CI/CD automates testing & deployment for your projects.", 
                    "Monitoring and logging are critical for production systems.",
                    "Caching significantly improves application performance."
                ]
            }
        )
        logger.info("Loaded csv file!")
        return df
    except Exception as err:
        logger.info(f"Error loading csv with error:{str(err)}")
        raise HTTPException(status_code=500, detail="Error loading data")
    
def get_data_summary():
    df = load_csv()
    return {
        "total_records":len(df), 
        "columns":list(df.columns), 
        "data_types":df.dtypes.to_dict()
    }