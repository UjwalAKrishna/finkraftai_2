import configparser
import ast
from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from API.llm import get_llm_model


# Config setup

config = configparser.ConfigParser()
config.read("config.properties")

lang = config["Language"]["lang"]
actions_cfg = ast.literal_eval(config["GenericSection"]["get_actions"])
lst_action = actions_cfg["actions"]
ALLOWED_ACTIONS = [a.upper() for a in lst_action]


# Schema for model output

class ActionResponse(BaseModel):
    action_option: str = Field(..., description=f"Must be one of {ALLOWED_ACTIONS}")

parser = PydanticOutputParser(pydantic_object=ActionResponse)


api = FastAPI()


@api.post("/request_info")
async def user_request(user_query: str = Form(...)):
    try:
        # Prompt template (system = rules, user = query)
        prompt = PromptTemplate(
            template=(
                "You are a STRICT action classifier.\n"
                f"Allowed actions: {ALLOWED_ACTIONS}\n"
                "From the user's query, return the SINGLE best action.\n"
                "Do not explain. Only return the parsed output.\n\n"
                "{format_instructions}"
            ),
            input_variables=[],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Build messages correctly
        system_prompt = prompt.format()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query)
        ]

        # Call Gemini LLM
        model_name = config["ModelName"]["gemini"]
        llm = get_llm_model(model_name)
        llm_resp = llm.invoke(messages)

        raw_text = getattr(llm_resp, "content", str(llm_resp)).strip()

        # Parse with the structured parser
        result: ActionResponse = parser.parse(raw_text)
        
         # if user ask for action based on the list of actions api calls will be done

        if result.action_option.upper() not in ALLOWED_ACTIONS:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid action '{result.action_option}'. Allowed: {ALLOWED_ACTIONS}",
            )

        return {"action_result": result.action_option.upper()}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



    
