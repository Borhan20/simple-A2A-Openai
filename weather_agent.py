# weather_agent.py
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
import os
from dotenv import load_dotenv

load_dotenv()  # if you need API keys later

app = FastAPI()

agent = Agent(
    model="openai:gpt-4.1",
    instructions="Provide weather forecasts based on a single location string.",
)

@agent.tool
async def get_weather(ctx: RunContext[str]) -> str:
    # ctx.prompt is the raw input string
    return f"Weather in {ctx.prompt}: Sunny, 25°C"

class A2ARequest(BaseModel):
    input: str

class A2AResponse(BaseModel):
    output: str

@app.post("/a2a", response_model=A2AResponse)
async def handle(req: A2ARequest):
    result = await agent.run(req.input)
    return {"output": result.output}
