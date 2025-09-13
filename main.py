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


with open("user_map.json", "r") as f:
    user_map = json.load(f)
# --------------------------
class ActionResponse(BaseModel):
    action_option: str = Field(..., description="Must be one of the allowed actions")


parser = PydanticOutputParser(pydantic_object=ActionResponse)


api = FastAPI()


def validate_user(user_id: int, password: str) -> str:
    for u in user_map:
        if u["user_id"] == user_id and u["password"] == password:
            return u["role"]
    raise HTTPException(status_code=401, detail="Invalid credentials")

@api.post("/role_info")
async def user_request(
    user_id: int = Form(...),
    password: str = Form(...),
    user_query: str = Form(...)
):
    try:
        # Step 1: Validate credentials
        role = validate_user(user_id, password).lower()  # normalize
        print(role)
        # Step 2: Restrict actions based on role
        if role not in config["GenericSection"]:
            raise HTTPException(status_code=403, detail=f"Role '{role}' not configured")

        actions_cfg = ast.literal_eval(config["GenericSection"][role])
        allowed = actions_cfg[role]
        print(allowed)
        # Step 3: Build prompt
        prompt = PromptTemplate(
            template=(
                "You are a STRICT action classifier of Ticket booking or Hotel Booking Website.\n"
                f"Role: {role}\n"
                f"Allowed actions for this role: {allowed}\n"
                "From the user's query, return the SINGLE best action.\n"
                "Do not explain. Only return the parsed output.\n\n"
                "{format_instructions}"
            ),
            input_variables=[],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        system_prompt = prompt.format()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query),
        ]

        # Step 4: Call Gemini LLM
        model_name = config["ModelName"]["gemini"]
        llm = get_llm_model(model_name)
        llm_resp = llm.invoke(messages)

        raw_text = getattr(llm_resp, "content", str(llm_resp)).strip()
        print("LLM RESPONSE:", raw_text)

        # Step 5: Parse and validate
        result: ActionResponse = parser.parse(raw_text)
        action = result.action_option

        if action not in allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Action '{action}' not allowed for role '{role}'",
            )

        return {"role": role, "action_result": action}


    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


