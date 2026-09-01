import asyncio

from dotenv import load_dotenv
from agents import Runner

from trading_council.agents.ava import ava, ava_reviewer
from trading_council.agents.betsy import betsy, betsy_reviewer
from trading_council.agents.camila import camila, camila_reviewer
from trading_council.agents.models import ResearchSession
from trading_council.agents.council import council

load_dotenv()


async def research(agent, prompt):
    result = await Runner.run(agent, prompt)
    return result.final_output


def print_proposal(proposal):
    print(f"\n{proposal.agent}'s Stock Picks")
    print("=" * 60)

    for idea in proposal.ideas:
        print(f"\n{idea.ticker} - {idea.company}")
        print(f"Conviction: {idea.conviction:.0%}")
        print(f"Thesis: {idea.thesis}")
        print("Risks:")

        for risk in idea.risks:
            print(f"  - {risk}")

        print("-" * 60)


async def main():
    prompt = """
    Research the current market and provide your five highest-conviction
    stock investment ideas based on your investment philosophy.
    """

    ava_result, betsy_result, camila_result = await asyncio.gather(
        research(ava, prompt),
        research(betsy, prompt),
        research(camila, prompt),
    )

    session = ResearchSession(
        ava=ava_result,
        betsy=betsy_result,
        camila=camila_result,
    )

    #print_proposal(session.ava)
    #print_proposal(session.betsy)
    #print_proposal(session.camila)

    council_prompt = f"""
    Review the following independent investment research from Ava, Betsy,
    and Camila.

    Ava's research:
    {session.ava.model_dump_json(indent=2)}

    Betsy's research:
    {session.betsy.model_dump_json(indent=2)}

    Camila's research:
    {session.camila.model_dump_json(indent=2)}

    Analyze the three proposals and conduct a council review.

    Identify:
    - Stocks multiple analysts agree on.
    - Important disagreements.
    - Particularly strong or weak investment theses.
    - Risks that may have been overlooked.
    - Which stocks you believe deserve consideration for the final portfolio.

    Then produce your final CouncilDecision.
    """

    council_result = await Runner.run(
        council,
        council_prompt,
    )

    decision = council_result.final_output

    print("\n\nCOUNCIL DISCUSSION")
    print("=" * 60)

    print("\nOverall Discussion:")
    print(decision.discussion)

    print("\n\nPoints for Ava:")
    for point in decision.points_for_ava:
        print(f"- {point}")

    print("\n\nPoints for Betsy:")
    for point in decision.points_for_betsy:
        print(f"- {point}")

    print("\n\nPoints for Camila:")
    for point in decision.points_for_camila:
        print(f"- {point}")

    ava_revision_prompt = f"""
    Review your original investment research after receiving feedback from
    the council.

    Your original research:
    {session.ava.model_dump_json(indent=2)}

    The council's feedback specifically for you:
    {decision.points_for_ava}

    Reconsider your five stock selections.

    You may keep your original portfolio if you still believe it is correct.
    You may replace stocks if the council's criticism has changed your
    conviction.

    You must finish with exactly five stocks.

    Clearly explain which stocks you changed, if any, and why.
    """

    betsy_revision_prompt = f"""
    Review your original investment research after receiving feedback from
    the council.

    Your original research:
    {session.betsy.model_dump_json(indent=2)}

    The council's feedback specifically for you:
    {decision.points_for_betsy}

    Reconsider your five stock selections.

    You may keep your original portfolio if you still believe it is correct.
    You may replace stocks if the council's criticism has changed your
    conviction.

    You must finish with exactly five stocks.

    Clearly explain which stocks you changed, if any, and why.
    """

    camila_revision_prompt = f"""
    Review your original investment research after receiving feedback from
    the council.

    Your original research:
    {session.camila.model_dump_json(indent=2)}

    The council's feedback specifically for you:
    {decision.points_for_camila}

    Reconsider your five stock selections.

    You may keep your original portfolio if you still believe it is correct.
    You may replace stocks if the council's criticism has changed your
    conviction.

    You must finish with exactly five stocks.

    Clearly explain which stocks you changed, if any, and why.
    """

    ava_revision_result, betsy_revision_result, camila_revision_result = await asyncio.gather(
        Runner.run(ava_reviewer, ava_revision_prompt),
        Runner.run(betsy_reviewer, betsy_revision_prompt),
        Runner.run(camila_reviewer, camila_revision_prompt),
    )

    ava_final = ava_revision_result.final_output
    betsy_final = betsy_revision_result.final_output
    camila_final = camila_revision_result.final_output

    print("\n\nAVA FINAL PORTFOLIO")
    print("=" * 60)
    print(ava_final.model_dump_json(indent=2))

    print("\n\nBETSY FINAL PORTFOLIO")
    print("=" * 60)
    print(betsy_final.model_dump_json(indent=2))

    print("\n\nCAMILA FINAL PORTFOLIO")
    print("=" * 60)
    print(camila_final.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())