"""
State management for the Deep Research agent using Pydantic models.
"""

from typing import TypedDict, Annotated, Sequence
from pydantic import BaseModel, Field
import operator


class Source(BaseModel):
    """A source document from research."""
    url: str
    title: str = ""
    content: str = ""
    relevance_score: float = 0.0


class Learning(BaseModel):
    """A learning extracted from research results."""
    content: str
    sources: list[str] = Field(default_factory=list)
    confidence: float = 1.0


class ResearchDirection(BaseModel):
    """A direction for further research."""
    goal: str
    rationale: str
    priority: int = 1


class ResearchState(TypedDict):
    """
    The state of the research process that flows through the LangGraph.
    
    This state is passed between nodes and accumulates information
    throughout the research process.
    """
    # Input parameters
    query: str
    breadth: int  # Number of search queries per iteration
    depth: int  # Number of research iterations
    follow_up_answers: list[str]
    
    # Current iteration state
    current_depth: int
    current_goal: str
    
    # Accumulated research data
    learnings: Annotated[list[Learning], operator.add]  # Accumulates across iterations
    next_directions: list[ResearchDirection]
    all_sources: Annotated[list[Source], operator.add]  # Accumulates across iterations
    
    # Generated queries and results (per iteration)
    search_queries: list[str]
    search_results: list[dict]
    
    # Final output
    final_report: str
    
    # Metadata
    total_tokens_used: int
    error: str | None


class GraphConfig(BaseModel):
    """Configuration for the research graph."""
    concurrency_limit: int = Field(default=3, ge=1, le=10)
    max_tokens_per_query: int = Field(default=4000)
    llm_temperature: float = Field(default=0.5, ge=0.0, le=2.0)
    enable_checkpointing: bool = Field(default=False)


def create_initial_state(
    query: str,
    breadth: int = 4,
    depth: int = 2,
    follow_up_answers: list[str] | None = None,
) -> ResearchState:
    """Create an initial research state."""
    return ResearchState(
        query=query,
        breadth=breadth,
        depth=depth,
        follow_up_answers=follow_up_answers or [],
        current_depth=0,
        current_goal=query,
        learnings=[],
        next_directions=[],
        all_sources=[],
        search_queries=[],
        search_results=[],
        final_report="",
        total_tokens_used=0,
        error=None,
    )
