import configparser
import ast
from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from API.llm import get_llm_model
import json

config = configparser.ConfigParser()
config.read("config.properties")

lang = config["Language"]["lang"]
info_url=config['APIENDPOINT']['get_info_api']

get_info_api
chat_sessions = {}

@api.post("/chat")
async def chat(
    user_id: int = Form(...),
    password: str = Form(...),
    user_message: str = Form(...),
):
   
    
    try:

        payload = {"user_id": user_id,"password": password,"user_query": user_message}
        response = requests.post(info_url, data=payload)
        
        return {"role":response.role,"res":response.action_result}
        


    except HTTPException:
        raise 
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
