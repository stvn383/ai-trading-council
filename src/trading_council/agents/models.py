from pydantic import BaseModel, Field

#Structured format for stock pick
class StockIdea(BaseModel):
    ticker: str = Field(description="Stock ticker symbol")
    company: str = Field(description="Company name")
    conviction: float = Field(
        ge=0,
        le=1,
        description="Confidence in the investment idea, from 0 to 1"
    )
    thesis: str = Field(description="Why the stock could perform well")
    risks: list[str] = Field(
        description="Major risks that could invalidate the thesis"
    )

#Structured format for stock pick list
class ResearchProposal(BaseModel):
    agent: str = Field(description="Name of the agent")
    ideas: list[StockIdea] = Field(
        min_length=5,
        max_length=5,
        description="List of five distinct stock ideas"
    )

class ResearchSession(BaseModel):
    ava: ResearchProposal
    betsy: ResearchProposal
    camila: ResearchProposal

class CouncilDiscussion(BaseModel):
    discussion: str = Field(
        description="Summary of the key arguments, disagreements, and insights from the discussion"
    )
    points_for_ava: list[str] = Field(
        description="Specific arguments or criticisms that Ava should consider"
    )
    points_for_betsy: list[str] = Field(
        description="Specific arguments or criticisms that Betsy should consider"
    )
    points_for_camila: list[str] = Field(
        description="Specific arguments or criticisms that Camila should consider"
    )