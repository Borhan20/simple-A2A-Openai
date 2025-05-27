import os
import asyncio
import logging
from httpx import AsyncClient
from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    GuardrailFunctionOutput,
    input_guardrail,
    output_guardrail,
    RunContextWrapper,
    TResponseInputItem,
)
from pydantic import BaseModel
# Configure logging at the module level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from agents import Agent, function_tool
from agents import Runner

load_dotenv()

# Downstream A2A URLs (override via env)
WEATHER_URL = os.getenv("WEATHER_URL", "http://localhost:8001/a2a")
HOTEL_URL   = os.getenv("HOTEL_URL",   "http://localhost:8002/a2a")


@function_tool
async def get_weather(location: str) -> str: # Changed ctx to location for clarity
    """
    Fetches the current weather forecast for a given location.
    Args:
        location: The city or region to get weather for.
    Returns:
        A string containing the weather information or an error message.
    """
    try:
        async with AsyncClient() as client:
            logging.info(f"Calling weather service at {WEATHER_URL} for {location}")
            resp = await client.post(WEATHER_URL, json={"input": location}, timeout=10.0)
            resp.raise_for_status()
            return resp.json().get("output", f"Weather service returned no output for {location}")
    except Exception as e:
        logging.error(f"Error calling weather service for {location}: {e}")
        return f"Failed to get weather for {location}: {e}"

@function_tool
async def find_hotels(location: str) -> str: # Changed ctx to location for clarity
    """
    Finds hotel suggestions for a given location.
    Args:
        location: The city or region to find hotels in.
    Returns:
        A string containing hotel suggestions or an error message.
    """
    try:
        async with AsyncClient() as client:
            logging.info(f"Calling hotel service at {HOTEL_URL} for {location}")
            resp = await client.post(HOTEL_URL, json={"input": location}, timeout=10.0)
            resp.raise_for_status()
            return resp.json().get("output", f"Hotel service returned no output for {location}")
    except Exception as e:
        logging.error(f"Error calling hotel service for {location}: {e}")
        return f"Failed to find hotels for {location}: {e}"
    



agent = Agent(
    # model="openai:gpt-4.1", # Assuming you have this configured externally or via env vars for the agent
    name="Trip Planner",
    instructions=(
        "You are a trip-planning assistant.  "
        "To get weather forecasts, use the `get_weather` tool with the location as its argument (e.g., get_weather('Paris')).  "
        "To fetch hotel options, use the `find_hotels` tool with the location as its argument (e.g., find_hotels('Paris')).  "
        "When asked about a trip, always identify the destination first. " # Added for clarity
        "Return the combined weather and hotel information in a clear, plain-text format. "
        "If a specific tool is not directly requested but contextually needed (e.g., 'plan a trip'), use both tools."
    ),
    tools=[get_weather, find_hotels],  # Allow tools to be called directly
  
)

async def main():
    print("Trip Planner REPL (type ‘exit’ to quit)\n")
    while True:
        text = input("Your query> ").strip()
        if text.lower() in ("exit", "quit"):
            break
        
        logging.info(f"User query: '{text}'")
        try:
            # Access the output via .text attribute
            result = await Runner.run(agent, input=text) # Use 'input=' for clarity with Runner.run
            print(f'result : {result.final_output}') # Changed .output to .text
        except Exception as e:
            logging.error(f"An error occurred during agent run: {e}")
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())