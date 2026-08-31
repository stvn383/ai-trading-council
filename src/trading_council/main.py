import asyncio
from dotenv import load_dotenv
from agents import Runner
from trading_council.agents.ava import ava

load_dotenv()

async def main():
    result = await Runner.run(
        ava,
        "Give me three stock investment ideas and explain your reasoning."
    )

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())