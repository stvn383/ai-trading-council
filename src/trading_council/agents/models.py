from pydantic import BaseModel, Field, model_validator

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
    risks: list[str] = Field(description="Major risks that could invalidate the thesis")

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
    discussion: str = Field(description="Summary of the key arguments, disagreements, and insights from the discussion")
    points_for_ava: list[str] = Field(description="Specific arguments or criticisms that Ava should consider")
    points_for_betsy: list[str] = Field(description="Specific arguments or criticisms that Betsy should consider")
    points_for_camila: list[str] = Field(description="Specific arguments or criticisms that Camila should consider")

class FinalPortfolio(BaseModel):
    agent: str = Field(description="Name of the agent")
    ideas: list[StockIdea] = Field(
        min_length=5,
        max_length=5,
        description="Exactly five final stock selections"
    )
    changed: bool = Field(description="Whether the agent changed any of its stock selections after the council discussion")
    changes: list[str] = Field(description="Specific changes made after the council discussion. Empty if no changes were made.")
    final_thesis: str = Field(description="Overall reasoning behind the final portfolio")

class PortfolioPosition(BaseModel):
    ticker: str = Field(description="Stock ticker symbol")
    weight: float = Field(
        ge=0,
        le=1,
        description="Portfolio weight as a decimal between 0 and 1"
    )
    reasoning: str = Field(description="Why the council assigned this portfolio weight")

class FinalCouncilDecision(BaseModel):
    discussion: str = Field(description="Final council assessment of the three revised portfolios")
    positions: list[PortfolioPosition] = Field(
        min_length=5,
        max_length=10,
        description="Final stocks selected for the paper portfolio"
    )
    @model_validator(mode="after")
    def validate_weights(self):
        total_weight = sum(position.weight for position in self.positions)
        if  abs(total_weight - 1.0) > 0.001:
            f"Portfolio weights must sum to 1.0, got {total_weight:.3f}"
        return self