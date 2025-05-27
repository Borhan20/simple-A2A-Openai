# hotel_agent.py
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

agent = Agent(
    model="openai:gpt-4.1",
    instructions="Suggest hotels based on a single location-and-budget string.",
)

@agent.tool
async def find_hotels(ctx: RunContext[str]) -> str:
    return f"Hotel suggestions for {ctx.prompt}: Hotel A, Hotel B, Hotel C"

class A2ARequest(BaseModel):
    input: str

class A2AResponse(BaseModel):
    output: str

@app.post("/a2a", response_model=A2AResponse)
async def handle(req: A2ARequest):
    result = await agent.run(req.input)
    return {"output": result.output}
